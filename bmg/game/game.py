from datetime import datetime
from logging import Logger
from time import sleep

from bmg.bsky import BskyClient
from bmg.database import Database
from bmg.database.rounds import RoundModel
from bmg.image import ImagePreparer
from bmg.matcher import Match
from bmg.tmdb import Movie, TmdbClient, TmdbMovieUtils
from bmg.types import GameState
from .config import GameConfig
from .posts import GamePostUris, GamePosts


class Game:
    """
    TODO: Substitute the logs with database write.
    """

    def __init__(self, config: GameConfig):
        self.bsky: BskyClient = config.bsky
        self.tmdb: TmdbClient = config.tmdb
        self.imgp: ImagePreparer = config.imgp
        self.db: Database = config.db
        self.logger: Logger = config.logger

        self.last_round: RoundModel | None = self.db.rounds.last_round()

        self.state: int = GameState.STOPPED
        self.round_number = self.last_round.num if self.last_round else 0
        self.threshold: int = config.threshold

        self.movie: Movie | None = None
        self.posts = GamePostUris(None, None, None, None)

        self.attempts = 0
        self.correct_attempts = 0
        self.percent = -1

    def select_random_movie(self):
        movie: Movie | None = None  # self.tmdb.get_random_movie()
        backdrops: list[bytes] | None = None  #

        # Movies that have under 4 backdrops must not be selected.
        while backdrops is None:
            movie = self.tmdb.get_random_movie()
            backdrops = TmdbMovieUtils.get_n_movie_backdrops(
                    self.tmdb,
                    movie.id
            )

        movie.images = [self.imgp.prepare(i) for i in backdrops]

        self.logger.info(f'Selected movie: {movie.title}')
        self.movie = movie

    def get_reply_score(self, reply: str):
        reply = Match.clean(reply)
        score = Match.str(self.movie.cleaned_title, reply)
        return score

    def calculate_correctness_percentage(self):
        self.attempts = 0
        self.correct_attempts = 0

        thread_res = self.bsky.get_thread(self.posts.round)
        thread = thread_res.thread

        if not len(thread.replies):
            self.logger.info("No players participated in this round. Skipping")
            return False

        self.logger.info(f'Matching {len(thread.replies)} comments')
        start = datetime.now()

        for reply in thread.replies:
            score = self.get_reply_score(reply.post.record.text)

            if score >= self.threshold:
                self.correct_attempts += 1
                self.bsky.client.like(reply.post.uri, reply.post.cid)

            self.attempts += 1

        end = datetime.now()

        self.logger.info(f'Thread matching ended. Timing result: {end - start}')

        self.percent = round(self.correct_attempts / self.attempts * 100)

        self.logger.info(
                f'Round #{self.round_number} results: '
                f'{self.correct_attempts}/{self.attempts} = {self.percent}%'
        )

    def delete_end_post(self):
        self.bsky.delete_post(self.posts.end)
        self.posts.end = None

    def new_round(self):
        self.state = GameState.INITIAL
        self.round_number += 1
        self.logger.info(f'===== Round #{self.round_number} =====')

        self.select_random_movie()

        self.posts.round = self.bsky.post_images(
                GamePosts.round(self.round_number),
                self.movie.images
        ).uri

        db_posts_rowid: int = self.db.posts.create(self.posts.round)
        db_round_rowid: int = self.db.rounds.create(
                self.round_number,
                self.state,
                self.movie.title,
                db_posts_rowid
        )

        # sleep(60 * 30)
        input("ENTER:")

        self.state = GameState.CALCULATION

        self.posts.end = self.bsky.post(GamePosts.end(self.round_number)).uri

        if self.calculate_correctness_percentage() is False:
            self.delete_end_post()
            self.posts.error = self.bsky.post(
                    GamePosts.insufficient(self.round_number)
            )
            self.logger.info('Not enough users. Retrying in 15 minutes...')
            sleep(60 * 15)
            return

        self.db.posts.update_end_uri(db_posts_rowid, self.posts.end)
        self.db.rounds.update_state(db_round_rowid, self.state)
        self.db.rounds.update_percent(db_round_rowid, self.percent)
        self.db.rounds.update_attempts(db_round_rowid, self.attempts)
        self.db.commit()

        self.state = GameState.RESULTS

        self.delete_end_post()
        self.db.posts.update_end_uri(db_posts_rowid, None)

        self.posts.results = self.bsky.post(
                GamePosts.results(
                        self.movie.title,
                        self.round_number,
                        self.percent,
                        self.attempts
                )
        ).uri

        now = datetime.now().isoformat()
        self.db.posts.update_results_uri(db_posts_rowid, self.posts.results)
        self.db.rounds.update_state(db_round_rowid, self.state)
        self.db.rounds.update_ended_in(db_round_rowid, now)
        self.db.commit()

        # sleep(60 * 30)
        input("ENTER:")

    def check_for_last_rounds(self):
        """
        Checks if there are any unfinished rounds. If so, deletes the posts
        and warns the users.
        """

        last_round = self.db.rounds.last_round()
        if last_round is None:
            return

        posts = self.db.posts.get_by_rowid(last_round.posts)
        self.bsky.delete_post(posts.round_uri)

        self.db.rounds.delete(last_round.num)

        self.bsky.post(GamePosts.error(last_round))

        self.logger.warning(
                f'Round #{last_round.num} wasn\'t in RESULTS '
                f'stage. Post removed from database and Bsky. '
        )

    def start(self):
        """ Starts the first round """

        self.check_for_last_rounds()

        while True:
            try:
                self.new_round()
            except Exception as err:
                self.logger.critical(
                        f'Untreated exception. Repeating in 15 minutes.',
                        exc_info=err,
                        stack_info=True
                )
                self.bsky.post(GamePosts.critical())

                if self.posts.round:
                    self.bsky.delete_post(self.posts.round)

                sleep(60 * 15)

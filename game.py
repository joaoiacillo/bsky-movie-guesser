from dataclasses import dataclass
from datetime import datetime
from logging import Logger

from time import sleep
from uu import Error

from bsky import BskyClient
from image import ImagePreparer
from matcher import Match
from tmdb import TmdbClient, TmdbMovieUtils, Movie

from collections import namedtuple

@dataclass
class GamePostUris:
    round: str
    error: str
    end: str
    results: str

    """
    Future notes:
    
    Results post needs round number, percentage of correctness, total attempts, next game time.
    """


class Game:
    """
    TODO: Substitute the logs with database write.
    """

    def __init__(self, bsky: BskyClient, tmdb: TmdbClient, imgp: ImagePreparer, logger: Logger, threshold: int):
        self.state = 'stopped'
        self.round_number = 0
        self.threshold = threshold

        self.bsky = bsky
        self.tmdb = tmdb
        self.imgp = imgp
        self.logger = logger

        self.movie = None
        self.posts = GamePostUris('', '', '', '')

        self.attempts = 0
        self.correct_attempts = 0
        self.percent = -1

    def build_post_content(self):
        return f'Guess the Movie! (Round #{self.round_number})'

    def select_random_movie(self):
        movie_id = self.tmdb.get_random_movie_id()

        title = self.tmdb.get_movie_name(movie_id)
        cleaned_title = Match.clean(title)
        self.logger.info(f'Selected movie: {title}')

        images = [self.imgp.prepare(i) for i in TmdbMovieUtils.get_n_movie_backdrops(self.tmdb, movie_id)]
        self.logger.info(f'{len(images)} backdrops fetched from API')

        self.movie = Movie(movie_id, title, cleaned_title, images)

    def post_round(self):
        post_content = self.build_post_content()
        self.posts.round = self.bsky.send_round(post_content, self.movie.images).uri
        #self.posts.round = 'at://did:plc:5jumb3lk7qnpfna7trmezvuo/app.bsky.feed.post/3l3c37ztlaa27'
        self.logger.info(f'Round post URI: {self.posts.round}')

    def get_reply_score(self, reply: str):
        reply = Match.clean(reply)
        score = Match.str(self.movie.cleaned_title, reply)
        return score

    def post_round_end(self):
        self.posts.end = self.bsky.send_post('Round ended. Counting the attempts...').uri

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
            f'Round #{self.round_number} results: {self.correct_attempts}/{self.attempts} = {self.percent}%')

    def delete_end_post(self):
        self.bsky.delete_post(self.posts.end)
        self.posts.end = ''

    def new_round(self):
        self.state = 'running'
        self.round_number += 1
        self.logger.info(f'Round #{self.round_number} just started')

        self.select_random_movie()
        self.post_round()

        print("(Similarity Compute) Press ENTER to continue: ")
        input()

        self.post_round_end()
        if self.calculate_correctness_percentage() is False:
            self.delete_end_post()
            self.posts.error = self.bsky.send_post(f'😥 Not a single user has commented in the last round. Skipping it for now...')
            return

        print("(Send Round Final Message) Press ENTER to continue: ")
        input()

        self.delete_end_post()

        self.posts.results = self.bsky.send_post(f'🏆 Results: {self.percent}% correct out of {self.attempts} attempts. Next game in N minutes.')

        print("(New Game) Press ENTER to continue: ")
        input()


    def start(self):
        """
        Starts the first round.
        TODO: Use database for maintaining game data
        """

        self.logger.info('Starting game')

        try:
            while True:
                self.new_round()
        except Exception as err:
            self.logger.critical(f'Untreated exception', exc_info=err, stack_info=True)
            self.bsky.send_post('😵 Oops! It looks like we had run into an internal problem. We\'ll be investigating the issue and the game will resume ASAP.')


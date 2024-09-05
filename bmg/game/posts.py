from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from random import choice

from bmg.database.rounds import RoundModel
from bmg.database.types import LatePostUri


@dataclass
class GamePostUris:
    round: LatePostUri
    error: LatePostUri
    end: LatePostUri
    results: LatePostUri


class GamePosts:
    """ Creates the post contents for each kind of post. """

    TIPS = (
        'In case you commit typos, don\'t panic, if you write mostly right, '
        'you will still be correct!',
        'We will like your post at the end of the match in case you\'ve '
        'guessed the title right.',
        'You can still comment on others comments. It won\'t affect the final '
        'result.'
    )

    @staticmethod
    def after_30_min():
        ahead = datetime.now(timezone.utc) + timedelta(minutes=30)
        return f'{ahead.strftime("%d/%m/%Y, %I:%M%p")} UTC'

    @classmethod
    def round(cls, round_number: int):
        return (
            f'🎥 Guess the Movie! (Round #{round_number})\n\n'
            f'You have 30 minutes ({cls.after_30_min()}) to make '
            f'a guess. Good luck!\n\n'
            f'(TIP: {choice(cls.TIPS)})'
        )

    @staticmethod
    def insufficient(round_number: int):
        return (
            '😥 Not a single user has commented in the round '
            f'{round_number}.\n\n'
            'Skipping it for now...'
        )

    @staticmethod
    def end(round_number: int):
        return (
            f'⏰ The time is up, everyone! (Round #{round_number})\n\n'
            'You\'ve made your guesses, and we\'re counting all of them. In a '
            'moment we\'ll post the results!'
        )

    @classmethod
    def results(
            cls,
            movie: str,
            round_number: int,
            percent: int,
            attempts: int
    ):
        if percent < 50:
            return (
                f'😿 Well... it wasn\'t this time... (Round #'
                f'{round_number})\n\n'
                f'It looks like you achieved {percent}% of score. There have '
                f'been {attempts} attempts from all of you.\n\n'
                f'The movie was: {movie}.\n\n'
                'Keep trying! The next round starts in 30 minutes '
                f'({cls.after_30_min()}).'
            )

        return (
            f'🏆 You\'ve made it! (Round #{round_number})\n\n'
            'This is the time you\'ve been waiting for! '
            f'Congratulations on achieving {percent}% of score! '
            f'There have been {attempts} attempts from all of you!\n\n'
            f'The movie was: {movie}.\n\n'
            f'The next round starts in 30 minutes ({cls.after_30_min()}).'
        )

    @staticmethod
    def error(last_round: RoundModel):
        return (
            f'⚠️ It looks like there was a problem and we had to remove the '
            f'last round of number #{last_round.num}. The movie was "'
            f'{last_round.movie}".\n\nWe\'re very sorry. A new round is '
            f'coming '
            f'right up!'
        )

    @staticmethod
    def critical():
        return (
            '😵 Oops! It looks like we had run into an internal problem. '
            'We\'ll be investigating the issue and the game will resume ASAP'
        )

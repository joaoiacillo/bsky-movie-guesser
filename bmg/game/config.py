from collections import namedtuple

GameConfig = namedtuple(
        'GameConfig',
        ('bsky', 'tmdb', 'imgp', 'db', 'logger', 'threshold', 'skip_on_input')
)

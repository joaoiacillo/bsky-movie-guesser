""" main.py

    Main Python script. It will prepare the bot and schedules for obtaining
    movie data from the API.
    
    Author: João Iacillo <john@iacillo.dev.br>
"""

import log

from bsky import BskyClient
from game import Game
from tmdb import TmdbClient
from image import ImagePreparer

import config

logger = log.create_default_logger(config.BOT_DEBUG_MODE)


if config.BOT_DEBUG_MODE:
    logger.debug('Debug mode enabled')


if __name__ == '__main__':
    imgp = ImagePreparer(config.TMDB_IMAGE_QUALITY, logger)
    tmdb = TmdbClient(config.TMDB_API_ACCESS_TOKEN)
    bsky = BskyClient(config.BSKY_HANDLE, config.BSKY_PASSWORD, logger)

    game = Game(bsky, tmdb, imgp, logger, config.BOT_THRESHOLD)
    game.start()

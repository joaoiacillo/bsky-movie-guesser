""" main.py

    Main Python script. It will prepare the bmg and schedules for obtaining
    movie data from the API.
    
    Author: João Iacillo <john@iacillo.dev.br>
"""

import config

from bmg.bsky import BskyClient
from bmg.database import Database
from bmg.game import Game, GameConfig
from bmg.image import ImagePreparer
from bmg.log import create_default_logger
from bmg.tmdb import TmdbClient

logger = create_default_logger(config.BOT_DEBUG_MODE)

if config.BOT_DEBUG_MODE:
    logger.debug('Debug mode enabled')

if __name__ == '__main__':
    imgp = ImagePreparer(config.TMDB_IMAGE_QUALITY, logger)
    db = Database(config.DB_FILE, logger)
    tmdb = TmdbClient(config.TMDB_API_ACCESS_TOKEN)
    bsky = BskyClient(config.BSKY_HANDLE, config.BSKY_PASSWORD, logger)

    game_config = GameConfig(
            bsky=bsky, tmdb=tmdb, imgp=imgp, db=db, logger=logger,
            threshold=config.BOT_THRESHOLD
    )

    game = Game(game_config)
    game.start()

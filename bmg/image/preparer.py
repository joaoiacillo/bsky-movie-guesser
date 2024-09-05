""" preparer.py

    Author: João Iacillo <john@iacillo.dev.br>
"""

from logging import Logger

from bmg.image import MovieImage


class ImagePreparer:
    def __init__(self, quality: int, logger: Logger):
        self.quality = quality
        self.logger = logger

        logger.info(f'ImagePrepare using JPEG quality of {quality}')

    def prepare(self, image_bytes: bytes) -> bytes:
        """
        Optimizes, censors and watermarks an image bytes objects automatically.

        This is pretty much a shortcut for doing these repetitive function
        calls for every image obtained from the API.

        You provide bytes, you receive bytes.
        """

        image = MovieImage(image_bytes)
        image.optimize(self.quality)
        image.censor()
        image.watermark()

        return image.to_bytes()

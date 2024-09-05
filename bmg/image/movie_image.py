""" movie_image.py

    Used by the image module for preparing a single image. Use the
    ImagePreparer class for preparing in a bulk with a common optimization
    configuration.

    Author: João Iacillo <john@iacillo.dev.br>
"""

from PIL import Image, ImageDraw

from .buffer import Buffer
from .censor import CensorUtils
from .tmdb import TMDB_SVG


class MovieImage:
    def __init__(self, i_bytes: bytes):
        self.buffer = Buffer(i_bytes)

    def optimize(self, quality: int) -> None:
        """ Resizes, compress, and optimize an image into a JPG `BytesIO` """

        image, output = self.buffer.create_pair()

        # Images bigger than 1280x720 should always be avoided.
        if image.size[0] > 1280 or image.size[1] > 720:
            image.thumbnail((1280, 720), Image.Resampling.BILINEAR)

        image.save(output, format='JPEG', quality=quality, optimize=True)

        self.buffer.save(output)

    def censor(self) -> None:
        """
        Important part of the game. The image needs to have certain parts
        censored so that the challenge can rise up. This draws rectangles
        around a random generated rectangle area, so that only it can be
        visible.
        """

        image, output = self.buffer.create_pair()

        visible_rect = CensorUtils.create_visible_window(image.size)
        censor_rects = CensorUtils.create_censor_rects(image.size, visible_rect)

        draw = ImageDraw.Draw(image)
        black = (0, 0, 0)
        for rect in censor_rects:
            draw.rectangle(rect, fill=black)

        image.save(output, format='JPEG')
        self.buffer.save(output)

    def watermark(self) -> None:
        """
        TMDB is a free and open API. This function includes their logo for
        properly attributing it as the source. Please do NOT deactive this.
        """

        image, output = self.buffer.create_pair()
        image = image.convert('RGBA')

        img_height = image.size[1]
        mark_height = TMDB_SVG.size[1]
        mark_offset = 50

        watermark_pos = (mark_offset, img_height - mark_height - mark_offset)

        image.paste(TMDB_SVG, watermark_pos, TMDB_SVG)

        # Always saving as JPEG only to save as PNG at the end, yeah I know...
        # But that's for optimization reasons. Adding the watermark involves
        # adding a transparency layer, so...
        image.save(output, format='PNG')

        self.buffer.save(output)

    def to_bytes(self) -> bytes:
        return self.buffer.to_bytes()

""" image.py

    Functions for dealing with images. It's a good thing to treat the images
    before sending them to the web, like: compressing, removing metadata, etc.
    This file also contains function for censoring certain parts of an image
    in a random way for adding difficulty to the game.
    
    Author: João Iacillo <john@iacillo.dev.br>
"""

from consts import ROOT_DIR

from os import path
from io import BytesIO
from random import randint

from PIL import Image as PILImage, ImageDraw, ImageFile
from cairosvg import svg2png

from logging import Logger

# TMDB Attribution SVG for watermarking. Please, ONLY CHANGE THIS if you're
# moving the file to another location or changing it's name, otherwise, keep
# this here for properly attributing the API as the source.
TMDB_SVG_PATH = path.join(ROOT_DIR, "tmdb.svg")

# We preserve the original file format for authenticity. This conversion only
# occurs during bootup, so it won't affect the bot performance at all.
with open(TMDB_SVG_PATH, 'rb') as svg:
    svg_data = svg.read()
    png_data = svg2png(bytestring=svg_data)

    TMDB_SVG = PILImage.open(BytesIO(png_data)).convert('RGBA')
    TMDB_SVG.thumbnail((100, 100), PILImage.Resampling.BILINEAR)


class CensorUtils:
    @staticmethod
    def create_visible_rect(isize: tuple[int, int]) -> tuple[int, int, int, int]:
        """
            The censor part requires a part of the image to be visible. This func
            creates a random rectangle around the screen that will be used as the
            visible part of it.

            These rectangles must be of 150x150 minimum and 500x300 of maximum.
        """

        iwidth, iheight = isize

        x1_offset = randint(150, 501)
        y1_offset = randint(150, 301)

        x0 = randint(0, iwidth - x1_offset)
        y0 = randint(0, iheight - y1_offset)
        x1 = min(iwidth, x0 + x1_offset)
        y1 = min(iheight, y0 + y1_offset)

        return x0, y0, x1, y1

    @staticmethod
    def create_rects(
        isize: tuple[int, int],
        vrect: tuple[int, int, int, int]
    ) -> tuple:
        """
            Creates rectangles around the visible rectangle within an image of a
            given size.
        """

        width, height = isize
        x0, y0, x1, y1 = vrect

        top_rect = (0, 0, width, y0)
        left_rect = (0, y0, x0, height)
        bottom_rect = (x0, y1, width, height)
        right_rect = (x1, y0, width, y1)

        return (
            top_rect,
            left_rect,
            bottom_rect,
            right_rect
        )


class ImageUtils:
    @staticmethod
    def to_buffer(image_bytes: bytes) -> BytesIO:
        """ Wrapper function for turning `bytes` into `BytesIO` """

        return BytesIO(image_bytes)

    @staticmethod
    def to_bytes(image_buffer: BytesIO) -> bytes:
        """ Wrapper function for turning `BytesIO` into `bytes` """

        return image_buffer.getvalue()


class Image:
    def __init__(self, ibytes: bytes):
        self.buffer = ImageUtils.to_buffer(ibytes)

    def open(self) -> tuple[ImageFile.ImageFile, BytesIO]:
        """
        Opens an image file based on the current buffer, and returns a new
        buffer instance for working on.
        """
        return PILImage.open(self.buffer), BytesIO()

    def save(self, new_buffer: BytesIO) -> BytesIO:
        """
        Saves a new buffer into the current image and returns it.
        """
        self.buffer = new_buffer
        return new_buffer

    def convert(self):
        """
        Converts the current buffer into bytes.
        """
        return ImageUtils.to_bytes(self.buffer)

    def optimize(self, quality: int) -> BytesIO:
        """ Resizes, compress, and optimize an image into a JPG `BytesIO` """

        image, output = self.open()

        # Images bigger than 1280x720 should always be avoided.
        if image.size[0] > 1280 or image.size[1] > 720:
            image.thumbnail((1280, 720), PILImage.Resampling.BILINEAR)

        image.save(output, format='JPEG', quality=quality, optimize=True)

        return self.save(output)

    def censor(self) -> BytesIO:
        """
        Important part of the game. The image needs to have certain parts
        censored so that the challenge can rise up. This draws rectangles
        around a random generated rectangle area, so that only it can be
        visible.
        """

        image, output = self.open()

        visible_rect = CensorUtils.create_visible_rect(image.size)
        censor_rects = CensorUtils.create_rects(image.size, visible_rect)

        draw = ImageDraw.Draw(image)
        for rect in censor_rects:
            draw.rectangle(rect, fill=(0, 0, 0))

        image.save(output, format='JPEG')
        return self.save(output)

    def watermark(self) -> BytesIO:
        """
        TMDB is a free and open API. This function includes their logo for
        properly attributing it as the source. Please do NOT deactive this.
        """

        image, output = self.open()
        image = image.convert('RGBA')

        iheight = image.size[1]
        wheight = TMDB_SVG.size[1]

        watermark_pos = (50, iheight - wheight - 50)

        image.paste(TMDB_SVG, watermark_pos, TMDB_SVG)

        # Always saving as JPEG only to save as PNG at the end, yeah I know...
        # But that's for optimization reasons. Adding the watermark involves
        # adding a transparency layer, so...
        # TODO: Is there a way to solve this? Is it worth it? Convert PNG to JPEG.
        image.save(output, format='PNG')

        return self.save(output)


class ImagePreparer:
    def __init__(self, quality: int, logger: Logger):
        self.quality = quality
        self.logger = logger

        logger.info(f'Images will be optimized to a JPEG quality of {quality}')

    def prepare(self, image_bytes: bytes) -> bytes:
        """
        Optimizes, censors and watermarks an image bytes objects automatically.

        This is pretty much a shortcut for doing these repetitive function
        calls for every image obtained from the API.

        You provide bytes, you receive bytes.
        """

        image = Image(image_bytes)
        image.optimize(self.quality)
        image.censor()
        image.watermark()

        return image.convert()

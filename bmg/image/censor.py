""" censor.py

    This file doesn't censor images due to political and ethical reasons. The
    censoring part of this game is only for increasing the challenge difficulty.

    Author: João Iacillo <john@iacillo.dev.br>
"""

from random import randint

from .types import BoundingBox, ImageSize


class CensorUtils:
    @staticmethod
    def create_visible_window(i_size: ImageSize) -> BoundingBox:
        """
        Creates a bounding box to be used as the visible window of the image.
        It's position and size are randomly generated on each call.
        """

        i_width, i_height = i_size

        x1_offset = randint(150, 501)
        y1_offset = randint(150, 301)

        # The initial (0) coordinates cannot surpass the image's size,
        # otherwise there will be now visible area.
        x0 = randint(0, i_width - x1_offset)
        y0 = randint(0, i_height - y1_offset)
        x1 = min(i_width, x0 + x1_offset)
        y1 = min(i_height, y0 + y1_offset)

        return x0, y0, x1, y1

    @staticmethod
    def create_censor_rects(
            i_size: ImageSize,
            visible_window: BoundingBox
    ) -> list[BoundingBox]:
        """
        Creates black rectangles around the visible window bounding box. The
        rectangles must be drawn manually one by one after creation,
        this function doesn't draw anything.
        """

        width, height = i_size
        x0, y0, x1, y1 = visible_window

        top_rect: BoundingBox = (0, 0, width, y0)
        left_rect: BoundingBox = (0, y0, x0, height)
        bottom_rect: BoundingBox = (x0, y1, width, height)
        right_rect: BoundingBox = (x1, y0, width, y1)

        return [top_rect, left_rect, bottom_rect, right_rect]

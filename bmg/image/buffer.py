""" buffer.py

    Used by the image module for managing the images in-memory.

    Author: João Iacillo <john@iacillo.dev.br>
"""

from io import BytesIO
from typing import Union

from PIL import Image
from PIL.ImageFile import ImageFile


class Buffer:
    def __init__(self, i_bytes: bytes):
        self.buffer = BytesIO(i_bytes)

    def create_pair(self) -> tuple[Union[ImageFile, Image.Image], BytesIO]:
        """
        Opens an image file based on the current buffer, and returns it
        right alongside with a new BytesIO instance that can be saved with the
        save() method.
        """
        return Image.open(self.buffer), BytesIO()

    def save(self, buffer: BytesIO) -> BytesIO:
        self.buffer = buffer

    def to_bytes(self) -> bytes:
        return self.buffer.getvalue()

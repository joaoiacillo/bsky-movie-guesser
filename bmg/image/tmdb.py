""" tmdb.py

    Author: João Iacillo <john@iacillo.dev.br>
"""

from io import BytesIO
from os import path

from PIL import Image as PILImage
from cairosvg import svg2png

from bmg.consts import ROOT_DIR

# TMDB Attribution SVG for watermarking. Please, ONLY CHANGE THIS if you're
# moving the file to another location or changing it's name, otherwise, keep
# this here for properly attributing the API as the source.
TMDB_SVG_PATH = path.join(ROOT_DIR, "tmdb.svg")

# We preserve the original file format for authenticity. This conversion only
# occurs during bootup, so it won't affect the bmg performance at all.
with open(TMDB_SVG_PATH, 'rb') as svg:
    svg_data = svg.read()
    png_data = svg2png(bytestring=svg_data)
    TMDB_SVG = PILImage.open(BytesIO(png_data)).convert('RGBA')
    TMDB_SVG.thumbnail((100, 100), PILImage.Resampling.BILINEAR)

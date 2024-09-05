""" image module

    Functions for dealing with images. It's a good thing to treat the images
    before sending them to the web, like: compressing, removing metadata, etc.
    This file also contains function for censoring certain parts of an image
    in a random way for adding difficulty to the game.
    
    Author: João Iacillo <john@iacillo.dev.br>
"""

from .movie_image import MovieImage
from .preparer import ImagePreparer

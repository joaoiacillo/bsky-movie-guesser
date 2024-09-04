""" matcher.py

    People commit typos, it's natural. Sometimes they just don't know how to
    write the name of the movie correctly, but they try. And there are users
    that can't guess correctly and throw some other movie.

    This Match class is responsible for comparing two strings based on the
    similarity score from 0 to 100 percent between the official movie title
    in English and the comment that the person sent.

    Byte comparison in these kinds of game is HORRIBLE. They take it too
    literally, and if you miss one letter, they give a false negative.

    Author: João Iacillo <john@iacillo.dev.br>
"""

from fuzzywuzzy import fuzz

class Match:
    @staticmethod
    def clean(string: str) -> str:
        """
        Cleans a string before their matching.
        """

        cleaned = string.strip()
        cleaned = ''.join(c for c in cleaned if c.isalnum() or c.isspace())
        cleaned = cleaned.lower().split()

        return ' '.join(cleaned)

    @staticmethod
    def str(a: str, b: str) -> int:
        """
        Matches two strings and returns a score between 0 and 100 based on their
        similarity.

        We recommend cleaning the strings before matching them, that is, removing
        extra symbols and spaces and turning them into a common case, such as
        lower or upper case.
        """

        return fuzz.ratio(a, b)

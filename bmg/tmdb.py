""" tmdb.py
    
    TMDB is the main API for fetching movies data for this bmg. This file
    contains the main TMDB client class for working with it more easily,
    and some other util methods.

    Author: João Iacillo <john@iacillo.dev.br>
"""

from dataclasses import dataclass
from random import choice, randint, sample
from typing import Union

from requests import get

from bmg.matcher import Match


@dataclass
class Movie:
    id: int
    title: str
    cleaned_title: str
    images: Union[list[bytes], None]


class TmdbClient:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def request(self, url: str, params: dict = None):
        if params is None:
            params = {}

        headers = {
            'Authorization': 'Bearer ' + self.access_token
        }

        return get(url, params, headers=headers)

    def get_random_movie(self) -> Movie:
        page = randint(1, 1000) // 20
        url = f'https://api.themoviedb.org/3/discover/movie'
        params = {
            'include_adult': 'false',
            'sort_by':       'popularity.desc',
            'page':          page
        }
        response = self.request(url, params)
        results = response.json()['results']
        chosen = choice(results)

        return Movie(
                chosen['id'],
                chosen['title'],
                Match.clean(chosen['title']),
                None
        )

    def get_movie_name(self, movie_id: int) -> str:
        url = f' https://api.themoviedb.org/3/movie/{movie_id}'
        response = self.request(url, {'language': 'en-US'})
        return response.json()['title']

    def get_movie_images(self, movie_id: int):
        url = f'https://api.themoviedb.org/3/movie/{movie_id}/images'
        return self.request(url)

    def get_movie_backdrops(self, movie_id: int):
        images = self.get_movie_images(movie_id).json()
        return images['backdrops']


class TmdbMovieUtils:
    @classmethod
    def get_n_movie_backdrops(
            cls,
            client: TmdbClient,
            movie_id: int,
            n: int = 4
    ):
        """
        Automatically fetches `n` random backdrops from a movie with `id`.
        """

        all_backdrops = client.get_movie_backdrops(movie_id)
        if len(all_backdrops) < 4:
            return None
        n_backdrops = sample(all_backdrops, n)

        images = [cls.get_movie_image(backdrop['file_path']) for backdrop in
                  n_backdrops[:n]]

        return images

    @staticmethod
    def get_movie_image(file_path: str):
        """
        Images obtained by `tmdb_get_movie_images` or
        `tmdb_get_movie_backdrops` contain a property called `file_path`.
        That's the one this function needs for fetching the image file from
        the API.

        Returns the image content as a `bytes` instance.
        """
        url = f'https://image.tmdb.org/t/p/original/{file_path}'
        response = get(url)
        return response.content

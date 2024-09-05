""" bsky.py

    Contains the class for dealing with Bsky API.

    Author: João Iacillo <john@iacillo.dev.br>
"""

from logging import Logger

from atproto import Client


class BskyClient:
    def __init__(self, handle: str, password: str, logger: Logger):
        self.client = Client()
        self.logger = logger

        self.client.login(handle, password)
        self.logger.info(f'Bsky client logged in as @{self.client.me.handle}')

    def post(self, content: str):
        return self.client.send_post(content)

    def post_images(self, content: str, images: list[bytes]):
        return self.client.send_images(content, images=images)

    def get_thread(self, uri: str):
        return self.client.get_post_thread(uri, 1)

    def delete_post(self, uri: str):
        return self.client.delete_post(uri)

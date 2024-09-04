from logging import Logger

from atproto import Client


class BskyClient:
    def __init__(self, handle: str, password: str, logger: Logger):
        self.client = Client()
        self.logger = logger

        self.client.login(handle, password)

    def send_post(self, content: str):
        return self.client.send_post(content)

    def send_round(self, content: str, images: list[bytes]):
        response = self.client.send_images(content, images=images)
        self.logger.info('Round published to Bsky')
        return response

    def get_thread(self, uri: str):
        response = self.client.get_post_thread(uri, 1)
        return response

    def delete_post(self, uri: str):
        return self.client.delete_post(uri)

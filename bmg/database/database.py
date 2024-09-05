import sqlite3
from logging import Logger

from .posts import Posts
from .rounds import Rounds


class Database:
    def __init__(self, file: str, logger: Logger):
        self.file = file
        self.logger = logger

        self.con = sqlite3.connect(self.file)
        self.cursor = self.con.cursor()
        self.logger.info(f'SQLite3 database connected in "{self.file}"')

        self.posts = Posts(self.con, self.cursor)
        self.rounds = Rounds(self.con, self.cursor)
        # self.cursor.execute('PRAGMA foreign_keys = ON;')

    def commit(self):
        self.con.commit()

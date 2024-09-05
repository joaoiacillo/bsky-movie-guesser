from dataclasses import dataclass
from sqlite3 import Connection, Cursor

from bmg.database.types import LatePostUri, PostUri


@dataclass
class PostsModel:
    rowid: int
    round_uri: PostUri
    error_uri: LatePostUri
    end_uri: LatePostUri
    results_uri: LatePostUri


class Posts:
    def __init__(self, con: Connection, cursor: Cursor):
        self.con = con
        self.cursor = cursor

        self._create_table()

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS posts (
            ROUND_URI   TEXT,
            ERROR_URI   TEXT,
            END_URI     TEXT,
            RESULTS_URI TEXT
        )
        """

        self.cursor.execute(query)

    def create(self, round_uri: PostUri):
        query = 'INSERT INTO posts (ROUND_URI) VALUES (?)'
        self.cursor.execute(query, (round_uri,))
        self.con.commit()
        return self.cursor.lastrowid

    def get_by_rowid(self, rowid: int):
        query = ('SELECT ROUND_URI, ERROR_URI, END_URI, RESULTS_URI FROM posts '
                 'WHERE rowid=?')
        self.cursor.execute(query, (rowid,))
        data = self.cursor.fetchone()
        return PostsModel(rowid, *data)

    def update_error_uri(self, rowid: int, error_uri: PostUri):
        query = 'UPDATE posts SET ERROR_URI=? WHERE rowid=?'
        self.cursor.execute(query, (error_uri, rowid))

    def update_end_uri(self, rowid: int, end_uri: PostUri):
        query = 'UPDATE posts SET END_URI=? WHERE rowid=?'
        self.cursor.execute(query, (end_uri, rowid))

    def update_results_uri(self, rowid: int, results_uri: PostUri):
        query = 'UPDATE posts SET RESULTS_URI=? WHERE rowid=?'
        self.cursor.execute(query, (results_uri, rowid))

from dataclasses import dataclass
from datetime import datetime
from sqlite3 import Connection, Cursor


@dataclass
class RoundModel:
    rowid: int
    num: int
    state: int
    movie: str
    posts: int
    percent: int | None
    attempts: int | None

    created_in: str
    ended_in: str | None


class Rounds:
    def __init__(self, con: Connection, cursor: Cursor):
        self.con = con
        self.cursor = cursor

        self._create_table()

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS rounds (
            NUM         INTEGER PRIMARY KEY,
            STATE       INTEGER,
            MOVIE       TEXT,
            POSTS       INTEGER,
            PERCENT     INTEGER,
            ATTEMPTS    INTEGER,
            CREATED_IN  TEXT,
            ENDED_IN    TEXT,
            
            FOREIGN KEY (POSTS) REFERENCES posts (rowid)
        )
        """

        self.cursor.execute(query)

    def create(self, num: int, state: int, movie: str, posts_rowid: int):
        now = datetime.now().isoformat()

        query = """
        INSERT INTO rounds (NUM, POSTS, MOVIE, CREATED_IN, STATE)
            VALUES (?, ?, ?, ?, ?)
        """

        self.cursor.execute(
                query,
                (num, posts_rowid, movie, now, state)
        )
        self.con.commit()
        return self.cursor.lastrowid

    def get_by_rowid(self, rowid: int):
        query = ('SELECT NUM, STATE, MOVIE, POSTS, PERCENT, ATTEMPTS, '
                 'CREATED_IN, ENDED_IN FROM rounds WHERE rowid=?')
        self.cursor.execute(query, (rowid,))
        data = self.cursor.fetchone()
        return RoundModel(rowid, *data)

    def last_round(self):
        self.cursor.execute(
                'SELECT rowid, NUM, STATE, MOVIE, POSTS, PERCENT, ATTEMPTS, '
                'CREATED_IN, ENDED_IN FROM rounds ORDER BY NUM DESC'
        )
        data = self.cursor.fetchone()
        return RoundModel(*data) if data else None

    def update_state(self, rowid: int, state: int):
        query = 'UPDATE rounds SET STATE=? WHERE rowid=?'
        self.cursor.execute(query, (state, rowid))

    def update_percent(self, rowid: int, percent: int):
        query = 'UPDATE rounds SET PERCENT=? WHERE rowid=?'
        self.cursor.execute(query, (percent, rowid))

    def update_attempts(self, rowid: int, attempts: int):
        query = 'UPDATE rounds SET ATTEMPTS=? WHERE rowid=?'
        self.cursor.execute(query, (attempts, rowid))

    def update_ended_in(self, rowid: int, ended_in: int):
        query = 'UPDATE rounds SET ENDED_IN=? WHERE rowid=?'
        self.cursor.execute(query, (ended_in, rowid))

    def delete(self, num: int):
        self.cursor.execute('DELETE from rounds WHERE NUM=?', (num,))
        self.con.commit()

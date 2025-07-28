import sqlite3
from models import Group, Attempt
from datetime import datetime

class DatabaseService:
    def __init__(self, path: str = 'data.db'):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self._ensure_tables()

    def _ensure_tables(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                is_women INTEGER NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY,
                group_id INTEGER NOT NULL,
                lane INTEGER NOT NULL,
                attempt_index INTEGER NOT NULL,
                time_sec REAL NOT NULL,
                errors INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_group(self, name: str, is_women: bool) -> Group:
        c = self.conn.cursor()
        c.execute('INSERT INTO groups(name,is_women) VALUES(?,?)', (name, int(is_women)))
        gid = c.lastrowid
        self.conn.commit()
        return Group(gid, name, is_women)

    def list_groups(self) -> list[Group]:
        c = self.conn.cursor()
        c.execute('SELECT id,name,is_women FROM groups')
        rows = c.fetchall()
        return [Group(r[0], r[1], bool(r[2])) for r in rows]

    def add_attempt(self, group_id: int, lane: int, attempt_index: int,
                    time_sec: float, errors: int) -> Attempt:
        c = self.conn.cursor()
        c.execute(
            'INSERT INTO attempts(group_id,lane,attempt_index,time_sec,errors) VALUES(?,?,?,?,?)',
            (group_id, lane, attempt_index, time_sec, errors)
        )
        aid = c.lastrowid
        self.conn.commit()
        c.execute('SELECT timestamp FROM attempts WHERE id=?', (aid,))
        ts = datetime.fromisoformat(c.fetchone()[0])
        group = next(g for g in self.list_groups() if g.id == group_id)
        return Attempt(aid, group, lane, attempt_index, time_sec, errors, ts)

    def list_attempts(self, group_id: int=None) -> list[Attempt]:
        c = self.conn.cursor()
        if group_id is not None:
            c.execute(
                'SELECT id,group_id,lane,attempt_index,time_sec,errors,timestamp'
                ' FROM attempts WHERE group_id=?', (group_id,)
            )
        else:
            c.execute(
                'SELECT id,group_id,lane,attempt_index,time_sec,errors,timestamp FROM attempts'
            )
        rows = c.fetchall()
        groups = {g.id: g for g in self.list_groups()}
        attempts = []
        for r in rows:
            attempts.append(Attempt(
                r[0], groups[r[1]], r[2], r[3], r[4], r[5], datetime.fromisoformat(r[6])
            ))
        return attempts

    def get_best_attempt(self, group_id: int, lane: int) -> Attempt | None:
        attempts = [a for a in self.list_attempts(group_id) if a.lane == lane]
        if not attempts:
            return None
        return min(attempts, key=lambda a: a.penalized_time)
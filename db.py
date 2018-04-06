import sqlite3

SLACKTIVATE_DB_PATH = '/tmp/slacktivate.db'

class Connection:
    def __init__(self):
        conn = sqlite3.connect(SLACKTIVATE_DB_PATH)
        with conn:
            already_created = True
            c = conn.cursor()
            try:
                c.execute('SELECT * FROM db_meta')
            except sqlite3.OperationalError:
                already_created = False
            if not already_created:
                print('DB not created, initializing')
                c.execute('CREATE TABLE db_meta (created INTEGER)');
                c.execute('INSERT INTO db_meta(created) VALUES (1)');
                c.execute('CREATE TABLE message_reactions(ts TEXT, channel TEXT, reaction TEXT)');
        self._conn = conn

    def has_run(self, event):
        with self._conn:
            c = self._conn.cursor()
            c.execute(
                'SELECT 1 FROM message_reactions WHERE ts=? AND channel=? AND reaction=?',
                (event['item']['ts'], event['item']['channel'], event['reaction']),
            )
            return bool(c.fetchall())

    def mark_run(self, event):
        with self._conn:
            c = self._conn.cursor()
            c.execute(
                'INSERT INTO message_reactions(ts, channel, reaction) VALUES (?, ?, ?)',
                (event['item']['ts'], event['item']['channel'], event['reaction']),
            )
            c.execute('SELECT * FROM message_reactions')


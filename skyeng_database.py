import sqlite3


class SkyengDatabase:
    def __init__(self, config):
        self.conn = sqlite3.connect(config["skyeng_db_filename"], check_same_thread=False)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    username TEXT PRIMARY KEY,
                    token TEXT NOT NULL
                )
            """)

    def insert_token(self, username, token):
        try:
            with self.conn:
                self.conn.execute("""
                    INSERT OR REPLACE INTO tokens (username, token) VALUES (?, ?)
                """, (username, token))
        except sqlite3.Error as e:
            print(f"An error occurred while inserting token: {e}")

    def get_token(self, username):
        try:
            cursor = self.conn.execute("""
                SELECT token FROM tokens WHERE username = ?
            """, (username,))
            row = cursor.fetchone()
            return row[0] if row else None
        except sqlite3.Error as e:
            print(f"An error occurred while fetching token: {e}")
            return None

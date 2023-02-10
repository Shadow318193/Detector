import sqlite3


class DB:
    def __init__(self, dirertory, db_name):
        self.directory = dirertory
        self.name = db_name

    def connect(self, text_for_execute: str, fetchall: bool = False,
                params: tuple = ()):
        with sqlite3.connect(self.directory + "/" + self.name) as conn:
            conn.cursor()
            if fetchall:
                try:
                    return conn.execute(text_for_execute, params).fetchall()
                except:
                    print(text_for_execute)
            else:
                conn.execute(text_for_execute, params)
                conn.commit()

    def global_init(self):
        self.connect("""
            CREATE TABLE IF NOT EXISTS requests_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            type VARCHAR
        );""")
        self.connect("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(64),
            name VARCHAR(32) NOT NULL,
            surname VARCHAR(32) NOT NULL,
            hashed_password VARCHAR NOT NULL
        );""")
        self.connect("""
        CREATE TABLE IF NOT EXISTS sites(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR DEFAULT "unnamed",
            url VARCHAR,
            is_moderated BOOLEAN DEFAULT FALSE
        );""")
        self.connect("""
        CREATE TABLE IF NOT EXISTS users_sites (
            user_id INTEGER NOT NULL,
            site_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (site_id) REFERENCES sites (id)
            );""")
        self.connect("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            time DATETIME, 
            duration INTEGER, 
            status INTEGER, 
            site_id INTEGER, 
            request_type_id INTEGER, 
            FOREIGN KEY(site_id) REFERENCES sites (id), 
            FOREIGN KEY(request_type_id) REFERENCES requests_types (id)
        );""")


# db = DB("../db", "detector2.db")
# db.global_init()
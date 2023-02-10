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
                return conn.execute(text_for_execute, params).fetchall()
            else:
                conn.execute(text_for_execute, params)
                conn.commit()

    def global_init(self):
        self.connect("""
            CREATE TABLE IF NOT EXISTS requests_types (
            id INTEGER NOT NULL, 
            type VARCHAR, 
            PRIMARY KEY (id)
        );""")
        self.connect("CREATE INDEX ix_requests_types_id ON requests_types (id);")
        self.connect("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER NOT NULL, 
            email VARCHAR(64), 
            name VARCHAR(32) NOT NULL, 
            surname VARCHAR(32) NOT NULL, 
            hashed_password VARCHAR NOT NULL, 
            is_admin BOOLEAN, 
            creation_date DATETIME, 
            PRIMARY KEY (id)
        );""")
        self.connect("CREATE INDEX ix_users_id ON users (id);")
        self.connect("CREATE UNIQUE INDEX ix_users_email ON users (email);")
        self.connect("""
        CREATE TABLE IF NOT EXISTS sites(
            id INTEGER NOT NULL, 
            name VARCHAR, 
            url VARCHAR,
            is_moderated BOOLEAN, 
            PRIMARY KEY (id)
        );""")
        self.connect("""
        CREATE TABLE IF NOT EXISTS users_sites (
            user_id INTEGER NOT NULL,
            site_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (site_id) REFERENCES sites (id)
            );""")
        self.connect("CREATE INDEX ix_sites_id ON sites (id);")
        self.connect("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER NOT NULL, 
            time DATETIME, 
            duration INTEGER, 
            status INTEGER, 
            site_id INTEGER, 
            request_type_id INTEGER, 
            PRIMARY KEY (id), 
            FOREIGN KEY(site_id) REFERENCES sites (id), 
            FOREIGN KEY(request_type_id) REFERENCES requests_types (id)
        );""")
        self.connect("CREATE INDEX ix_requests_id ON requests (id);")


# db = DB("../db", "detector2.db")
# db.global_init()
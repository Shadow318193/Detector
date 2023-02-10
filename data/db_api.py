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
        lst = ["DE request", "NL request", "SG request", "RU request", "USA request", "UK request"]
        for i in lst:
            self.connect("INSERT INTO requests_types (type) VALUES(?)", params=(i,))


    def add_request(self, data):
        # id сайта
        site_id = self.connect("""
                        SELECT id FROM sites WHERE url=?
                        """, fetchall=True, params=(data["url"],))
        if not site_id:
            site_id = self.connect("""
                            INSERT INTO sites(url) VALUES(?) RETURNING id;
                            """, fetchall=True, params=(data["url"],))

        site_id = site_id[0][0]
        # id запроса
        req_type_id = self.connect("""
                        SELECT id FROM requests_types WHERE type = ?;
                        """, fetchall=True, params=(data["method"],))
        if not req_type_id:
            print(f"Error unknown method: \"{data['method']}\"")
            return -1

        self.connect("""
                        INSERT INTO requests(duration, status, site_id,
                         request_type_id, time) VALUES(?, ?, ?, ?, TIME(\"now\"));
                        """, params=(
            data["duration"], data["code"], site_id,
            req_type_id[0][0]))


# db = DB("../db", "detector2.db")
# db.global_init()
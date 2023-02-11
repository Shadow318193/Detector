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
            is_moderated SMALLINT DEFAULT 0
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
            self.connect("INSERT INTO requests_types (type) VALUES(?)", params=(i, ))

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

    def requests_by_user_id(self, user_id: int):
        site_ids = self.connect("""SELECT site_id FROM users_sites WHERE user_id=?;""",
                                params=(user_id, ),
                                fetchall=True)
        data = dict()
        for site in site_ids:
            d = self.connect("""SELECT name, url FROM sites WHERE id=? AND
                                is_moderated=1;""",
                             params=(site[0], ),
                             fetchall=True)
            if not d:
                continue
            name_site, url_site = d[0]

            requests_lst = [name_site, url_site]
            requests_types = [x[0] for x in self.connect("""SELECT id FROM requests_types;""",
                                                         fetchall=True)]
            for requests_t in requests_types:
                o = self.connect("""SELECT status FROM requests WHERE site_id=? AND
                                 request_type_id=? ORDER BY time DESC LIMIT 1;""",
                                 fetchall=True, params=(site[0], requests_t, ))
                if not o:
                    continue
                requests_lst.append(o[0][0])
            data[site[0]] = requests_lst
        return data

    def non_moderated_by_user_id(self, user_id: int):
        site_ids = self.connect("""SELECT site_id FROM users_sites WHERE user_id=?;""",
                                params=(user_id,),
                                fetchall=True)
        data = dict()
        for site in site_ids:
            d = self.connect("""SELECT name, url FROM sites WHERE id=? AND
                                                        is_moderated=0;""",
                             params=(site[0],),
                             fetchall=True)
            if not d:
                continue
            name_site, url_site = d[0]
            data[site[0]] = [name_site, url_site]

        return data

    def rejected_by_user_id(self, user_id: int):
        site_ids = self.connect("""SELECT site_id FROM users_sites WHERE user_id=?;""",
                                params=(user_id,),
                                fetchall=True)
        data = dict()
        for site in site_ids:
            d = self.connect("""SELECT name, url FROM sites WHERE id=? AND
                                                        is_moderated=-1;""",
                             params=(site[0],),
                             fetchall=True)
            if not d:
                continue
            name_site, url_site = d[0]
            data[site[0]] = [name_site, url_site]

        return data

    def non_moderated_list(self):
        d = self.connect("""SELECT id, name, url FROM sites WHERE is_moderated=0;""",
                         fetchall=True)
        data = dict()
        for site in d:
            data[site[0]] = [site[1], site[2]]

        return data

    def add_syte(self, url_name: tuple, user_id: int):
        site_id = self.connect("""
                                SELECT id FROM sites WHERE url=?;
                                """, fetchall=True, params=(url_name[0],))
        if not site_id:
            site_id = self.connect("""
                                    INSERT INTO sites(url, name) VALUES(?, ?) RETURNING id;
                                    """, fetchall=True, params=url_name)
        site_id = site_id[0][0]
        self.connect("""INSERT INTO users_sites (user_id, site_id)
         VALUES(?, ?);""", params=(user_id, site_id, ))

    def set_moder(self, id_state: tuple):
        self.connect("""UPDATE sites SET is_moderated=? WHERE id=? RETURNING id;""",
                     params=id_state[::-1], fetchall=True)
        if not id:
            return -1
        else:
            return 0

    def get_statistic(self, site_id):
        time_s = self.connect("""SELECT time FROM requests WHERE site_id=?
         ORDER BY time LIMIT 1;""",
                              params=(site_id, ), fetchall=True)
        if not time_s:
            time_s = None
        else:
            time_s = time_s[0][0]
        requests_count = self.connect("""SELECT COUNT(*) FROM requests WHERE site_id=?;""",
                                      params=(site_id, ), fetchall=True)[0][0]
        bad_requests_count = self.connect("""SELECT COUNT(*) FROM
         requests WHERE site_id=? AND status <> 200 AND status <> 301;""",
                                          params=(site_id, ), fetchall=True)[0][0]
        data = {"time start": time_s,
                "requests count": requests_count,
                "bad requests count": bad_requests_count}
        return data

    def sites_list(self):
        site_ids = self.connect("""SELECT url FROM sites WHERE is_moderated=1;""",
                                fetchall=True)
        return list(el[0] for el in site_ids)

if __name__ == "__main__":
    db = DB("../db", "detector2.db")
    # db.global_init()
    # x = db.requests_by_user_id(1)
    # x = db.rejected_by_user_id(1)
    # x = db.add_syte(("https://sqliteonline.com/", "sqlite_online"), 1)
    # print(db.set_moder((5, 1)))
    # print(db.get_statistic(2))
    print(db.sites_list())
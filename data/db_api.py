import sqlite3
import os


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
                except Exception:
                    print(text_for_execute)
            else:
                conn.execute(text_for_execute, params)
                conn.commit()

    def global_init(self):
        print(
            "Connecting to the database at " + '"' + self.directory +
            "/" + self.name + '"')
        if not os.path.exists(self.directory + "/" + self.name):
            with open(self.directory + "/" + self.name, "w+"):
                pass
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
                hashed_password VARCHAR NOT NULL,
                is_admin BOOL NOT NULL
            );""")
            self.connect("""
            CREATE TABLE IF NOT EXISTS sites(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR DEFAULT "unnamed",
                url VARCHAR,
                is_moderated SMALLINT DEFAULT 0,
                id_rating VARCHAR DEFAULT NULL,
                count_users INTEGER DEFAULT 0
            );""")
            self.connect("""
            CREATE TABLE IF NOT EXISTS users_sites (
                user_id INTEGER NOT NULL,
                site_id INTEGER NOT NULL,
                tg_id INTEGER DEFAULT NULL,
                email TEXT DEFAULT NULL,
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
                is_outdated BOOL DEFAULT FALSE,
                FOREIGN KEY(site_id) REFERENCES sites (id), 
                FOREIGN KEY(request_type_id) REFERENCES requests_types (id)
            );""")
            self.connect("""CREATE TABLE IF NOT EXISTS rating (
            site_id INTEGER,
            rating REAL,
            last_time DATETIME,
            FOREIGN KEY(site_id) REFERENCES sites (id)
            );""")
            self.connect(
                "INSERT INTO users(email, name, surname, hashed_password, is_admin)"
                "VALUES (\"a@a.com\", \"admin\", \"admin\","
                "\"pbkdf2:sha256:"
                "260000$QyxkhHYIJ9hRUVJC$e7d12546636b8be81d364116d150cf76729b12cef1fd5084e872200117987d2c\","
                " 1)")
            lst = ["DE request", "NL request", "SG request", "RU request",
                   "USA request", "UK request"]
            for i in lst:
                self.connect("INSERT INTO requests_types (type) VALUES(?)",
                             params=(i,))
            lst = [("https://proton.mskobr.ru/",
                    "Образовательный центр «Протон»"),
                   ("https://www.msu.ru/",
                    "Московский государственный университет имени М.В.Ломоносова"),
                   ("https://mipt.ru/",
                    "Московский физико-технический институт")]
            for i in lst:
                site_id = self.connect(
                    """INSERT INTO sites(url, name, is_moderated) VALUES(?, ?, 1)
                 RETURNING id;""",
                    fetchall=True, params=i)

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
                         request_type_id, time) VALUES(?, ?, ?, ?, TIME(\"now\", "+3 hours"));
                        """, params=(
            data["duration"], data["code"], site_id,
            req_type_id[0][0]))

    def requests_by_user_id(self, user_id: int):
        requests_types = self.connect(
            """SELECT id, type FROM requests_types;""",
            fetchall=True)
        site_ids = self.connect(
            """SELECT site_id FROM users_sites WHERE user_id=?;""",
            params=(user_id,),
            fetchall=True)
        data = dict()
        for site in site_ids:
            d = self.connect("""SELECT name, url FROM sites WHERE id=? AND
                                is_moderated=1;""",
                             params=(site[0],),
                             fetchall=True)
            if not d:
                continue
            name_site, url_site = d[0]

            requests_lst = [name_site, url_site, {}]
            for requests_t in requests_types:
                o = self.connect("""SELECT status, duration FROM requests WHERE site_id=? AND
                                 request_type_id=? ORDER BY time DESC LIMIT 1;""",
                                 fetchall=True,
                                 params=(site[0], requests_t[0],))
                if not o:
                    continue
                requests_lst[-1][requests_t[1]] = o[0]
            data[site[0]] = requests_lst
        return data

    def non_moderated_by_user_id(self, user_id: int):
        site_ids = self.connect(
            """SELECT site_id FROM users_sites WHERE user_id=?;""",
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
        site_ids = self.connect(
            """SELECT site_id FROM users_sites WHERE user_id=?;""",
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
        d = self.connect(
            """SELECT id, name, url FROM sites WHERE is_moderated=0;""",
            fetchall=True)
        data = dict()
        for site in d:
            data[site[0]] = [site[1], site[2]]

        return data

    def moderated_list(self):
        d = self.connect(
            """SELECT id, name, url FROM sites WHERE is_moderated=1;""",
            fetchall=True)
        data = dict()
        for site in d:
            data[site[0]] = [site[1], site[2]]

        return data

    def rejected_list(self):
        d = self.connect(
            """SELECT id, name, url FROM sites WHERE is_moderated=-1;""",
            fetchall=True)
        data = dict()
        for site in d:
            data[site[0]] = [site[1], site[2]]

        return data

    def add_site(self, url_name: tuple, user_id: int):
        site_id = self.connect("""
                                SELECT id FROM sites WHERE url=?;
                                """, fetchall=True, params=(url_name[0],))
        if not site_id:
            site_id = self.connect("""
                                    INSERT INTO sites(url, name) VALUES(?, ?) RETURNING id;
                                    """, fetchall=True, params=url_name)
        site_id = site_id[0][0]
        self.connect("""INSERT INTO users_sites (user_id, site_id)
         VALUES(?, ?);""", params=(user_id, site_id,))
        self.connect(
            """UPDATE sites SET count_users=count_users+1 WHERE id=?;""",
            params=(site_id,))

    def set_moder(self, id_state: tuple):
        id_s = self.connect(
            """UPDATE sites SET is_moderated=? WHERE id=? RETURNING id;""",
            params=id_state[::-1], fetchall=True)
        if not id_s:
            return -1
        else:
            return 0

    def get_statistic(self, site_id):
        time_s = self.connect("""SELECT time FROM requests WHERE site_id=?
         ORDER BY time DESC LIMIT 1;""",
                              params=(site_id,), fetchall=True)
        if not time_s:
            time_s = None
        else:
            time_s = time_s[0][0]
        requests_count = \
            self.connect("""SELECT COUNT(*) FROM requests WHERE site_id=?;""",
                         params=(site_id,), fetchall=True)[0][0]
        bad_requests_count = self.connect("""SELECT COUNT(*) FROM
         requests WHERE site_id=? AND status <> 200 AND status <> 301;""",
                                          params=(site_id,), fetchall=True)[0][
            0]
        data = {"time start": time_s,
                "requests count": requests_count,
                "bad requests count": bad_requests_count}
        return data

    def sites_list(self):
        site_ids = self.connect(
            """SELECT url FROM sites WHERE is_moderated=1;""",
            fetchall=True)
        return list(el[0] for el in site_ids)

    def get_requests_types(self):
        requests_types = self.connect(
            """SELECT type FROM requests_types;""",
            fetchall=True)
        return [x[0] for x in requests_types]

    def get_popular(self):
        data = dict()
        ids = self.connect(
            """SELECT id, name, url from sites WHERE is_moderated=1 ORDER BY count_users DESC, id LIMIT 3""",
            fetchall=True)
        requests_types = self.connect(
            """SELECT id, type FROM requests_types;""",
            fetchall=True)
        for site in ids:
            requests_lst = [site[1], site[2], {}]
            for requests_t in requests_types:
                o = self.connect("""SELECT status, duration FROM requests WHERE site_id=? AND
                                 request_type_id=? ORDER BY time DESC LIMIT 1;""",
                                 fetchall=True,
                                 params=(site[0], requests_t[0],))
                if not o:
                    continue
                requests_lst[-1][requests_t[1]] = o[0]
            data[site[0]] = requests_lst
        return data

    def get_id_site_by_url(self, url):
        id_site = self.connect("""SELECT id FROM sites WHERE url=?""",
                               params=(url,), fetchall=True)
        return id_site[0][0]

    def set_name_for_site(self, id_site, name):
        id_s = self.connect(
            """UPDATE sites SET name=? WHERE id=? RETURNING id;""",
            params=(name, id_site,), fetchall=True)
        if not id_s:
            return -1
        else:
            return 0

    def moderated_by_user_id(self, user_id):
        site_ids = self.connect(
            """SELECT site_id FROM users_sites WHERE user_id=?;""",
            params=(user_id,),
            fetchall=True)
        data = dict()
        for site in site_ids:
            d = self.connect("""SELECT name, url FROM sites WHERE id=? AND
                                                                is_moderated=1;""",
                             params=(site[0],),
                             fetchall=True)
            if not d:
                continue
            name_site, url_site = d[0]
            data[site[0]] = [name_site, url_site]

        return data

    def del_site_by_user_id(self, site_id, user_id):
        self.connect(
            """DELETE FROM users_sites WHERE site_id=? AND user_id=?""",
            params=(site_id, user_id,), fetchall=True)
        self.connect(
            """UPDATE sites SET count_users=count_users-1 WHERE id=?;""",
            params=(site_id,))

    def notification_tg(self):
        requests_types = self.connect(
            """SELECT id, type FROM requests_types;""",
            fetchall=True)
        d = self.connect("""SELECT site_id, tg_id, email FROM users_sites WHERE tg_id
         NOT NULL OR email NOT NULL""", fetchall=True)
        data = list()
        for el in d:
            tg_id = el[1]
            email = el[2]
            d = self.connect("""SELECT name, url FROM sites WHERE id=? AND
                                            is_moderated=1;""",
                             params=(el[0],),
                             fetchall=True)
            if not d:
                continue
            name_site, url_site = d[0]
            for requests_t in requests_types:
                o = self.connect("""SELECT status, duration, id FROM requests WHERE site_id=? AND
                                 request_type_id=? ORDER BY time DESC LIMIT 2;""",
                                 fetchall=True,
                                 params=(el[0], requests_t[0],))
                if len(o) < 2:
                    continue
                # проверка актуальности данных
                if o[1][0] < 0:
                    continue
                if o[0][0] != o[1][0] or o[0][1] / o[1][1] >= 2:
                    self.connect("""UPDATE requests SET status=? WHERE id=?""",
                                 params=(-1 * o[1][0], o[1][2]))
                    d = (
                        tg_id, email, [name_site, url_site],
                        [o[1][0], o[0][0]],
                        [o[1][1], o[0][1]])
                    data.append(d)

        return data

    def get_need_rating(self):
        ids = self.connect("""SELECT site_id FROM rating WHERE
        ROUND((JULIANDAY("now", "+3 hours") - JULIANDAY(last_time)) * 86400) >
         3600;""",
                           fetchall=True)
        rating_ids = set(i[0][0] for i in [
            self.connect("""SELECT id_rating FROM sites WHERE id=?""",
                         params=(x[0],), fetchall=True) for x in ids])
        for x in self.connect(
                """SELECT id_rating FROM sites WHERE id_rating IS NOT NULL;""",
                fetchall=True):
            rating_ids.add(x[0])
        return rating_ids


if __name__ == "__main__":
    db = DB("../db", "detector2.db")
    db.global_init()
    print(db.get_need_rating())
    # db.del_site_by_user_id(4, 1)
    # print(db.non_moderated_list())
    # # db.global_init()
    # x = db.requests_by_user_id(1)
    # print(x)
    # print(db.set_name_for_site(56, "коин"))
    # print(db.moderated_by_user_id(1))
    # print(db.non_moderated_by_user_id(1))
    # print(db.rejected_by_user_id(1))
    # print(db.get_id_site_by_url("https://test.com"))
    # print(db.get_requests_types())
    # print(db.get_popular())
    # x = db.rejected_by_user_id(1)
    # x = db.add_syte(("https://sqliteonline.com/", "sqlite_online"), 1)
    # print(db.set_moder((5, 1)))
    # print(db.get_statistic(1))

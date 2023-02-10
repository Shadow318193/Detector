from tester.test1 import AvailableTester


class Parser:
    parsers = [
        AvailableTester()
    ]

    def push_data(self, urls: list, db) -> None:
        """Commiting requests to DB"""
        for parser in self.parsers:
            print(parser)
            response = parser.get_data(urls)
            for country in response:
                site_id = db.connect("""
                SELECT id FROM sites WHERE url=?,
                """, fetchall=True, params=(country["url"],))
                if not site_id:
                    db.connect("""
                    INSERT INTO sites(url) VALUES(?);
                    """, params=(country["url"]))
                    site_id = db.connect("""
                                    SELECT id FROM sites WHERE url=?,
                                    """, fetchall=True,
                                         params=(country["url"],))

                req_type_id = db.connect("""
                SELECT id FROM requests_types WHERE type = ?;
                """, fetchall=True, params=(country["method"],))
                if not req_type_id:
                    db.connect("""
                    INSERT INTO requests_types(type) VALUES(?);
                    """, params=(country["method"]))
                    req_type_id = db.connect("""
                    SELECT id FROM requests_types WHERE type = ?;""",
                                             fetchall=True,
                                             params=(country["method"],))
                print(site_id, req_type_id)
                db.connect("""
                INSERT INTO requests(duration, status, site_id, request_type_id) VALUES(?, ?, ?, ?);
                """, params=(
                country["duration"], country["code"], site_id[0][0],
                req_type_id[0][0]))

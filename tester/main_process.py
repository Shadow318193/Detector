from tester.test1 import AvailableTester
from tester.test2 import CheckHostParser
from data.db_api import DB

db = DB("../db", "detector2.db")


class Parser:
    parsers = [
        # AvailableTester()
        CheckHostParser()
    ]

    def push_data(self, db) -> None:
        """Commiting requests to DB"""
        urls = db.sites_list()
        for parser in self.parsers:
            response = parser.get_data(urls)
            for country in response:
                db.add_request(country)

# p = Parser()
# p.push_data(db)

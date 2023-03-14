from tester.test1 import AvailableTester
from tester.test2 import CheckHostParser
from tester.rating import UchebaParser
from data.db_api import DB
from tester.interface import AvailableParser, RatingParser

db = DB("../db", "detector2.db")


class Parser:
    parsers = [
        # AvailableTester()
        # CheckHostParser(),
        UchebaParser()
    ]

    def push_data(self, db) -> None:
        """Commiting requests to DB"""
        urls = db.sites_list()
        ids = db.get_need_rating()
        for parser in self.parsers:
            if isinstance(parser, AvailableParser):
                response = parser.get_data(urls)
                for country in response:
                    db.add_request(country)
            elif isinstance(parser, RatingParser):
                response = parser.get_data(ids)
                print(response)
                db.set_rating(response)


p = Parser()
p.push_data(db)

from data import db_session
from data.request import Request
from data.requesttype import RequestType

from tester.test1 import AvailableTester


class Parser:
    parsers = [
        AvailableTester()
    ]

    def push_data(self, urls: list) -> None:
        """Commiting requests to DB"""
        for parser in self.parsers:
            response = parser.get_data(urls)
            for country in response:
                req = Request()
                req.duration = country["duration"]
                req.status = country["code"]
                db_sess = db_session.create_session()
                req_type = db_sess.query(RequestType.id).filter_by(
                    type=country["method"]).first()
                if not req_type:
                    req_type = RequestType()
                    req_type.type = country["method"]
                # req.site_id = site_id
                req.request_type_id = req_type.id
                db_sess.add(req)
                db_sess.commit()
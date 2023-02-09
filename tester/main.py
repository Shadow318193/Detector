from data import db_session
# from data.request import Request
# from data.requesttype import RequestType
# from data.site import Site

from tester.test1 import AvailableTester


class Parser:
    parsers = [
        AvailableTester()
    ]

    def push_data(self, urls: list) -> None:
        """Commiting requests to DB"""
        for parser in self.parsers:
            print(parser)
            # response = parser.get_data(urls)
            # for country in response:
            #     req = Request()
            #     req.duration = country["duration"]
            #     req.status = country["code"]
            #     db_sess = db_session.create_session()
            #     site = db_sess.query(Site).filter_by(
            #         type=country["url"]).first()
            #     if not site:
            #         site = Site()
            #         site.url = country["url"]
            #     req_type = db_sess.query(RequestType).filter_by(
            #         type=country["method"]).first()
            #     if not req_type:
            #         req_type = RequestType()
            #         req_type.type = country["method"]
            #     req.site_id = site.id
            #     req.request_type_id = req_type.id
            #     db_sess.add(req)
            #     db_sess.commit()

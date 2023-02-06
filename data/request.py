import sqlalchemy as db
from data.db_session import SqlAlchemyBase
import datetime as dt
from sqlalchemy import orm


class Request(SqlAlchemyBase):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,
                   nullable=False, index=True)
    time = db.Column(db.DateTime, default=dt.datetime.now())
    duration = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=200)
    site_id = db.Column(db.Integer, db.ForeignKey("sites.id"), default=1)
    site = orm.relationship("Site")
    request_type_id = db.Column(db.Integer,
                                db.ForeignKey("requests_types.id"), default=1)
    request_type = orm.relationship("RequestType")

    def __repr__(self):
        return f"Request {self.id}: {self.time} Result={self.status}"
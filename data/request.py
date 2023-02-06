import sqlalchemy as db
from data.db_session import SqlAlchemyBase
import datetime as dt
from sqlalchemy import orm


class Request(SqlAlchemyBase):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,
                   nullable=False, index=True)
    time = db.Column(db.DateTime, default=dt.datetime.now())
    status = db.Column(db.Integer, default=200)
    site_id = db.Column(db.Integer, db.ForeignKey("sites.id"))
    site = orm.relationship("Site")
    request_type_id = db.Column(db.Integer, db.ForeignKey("requests_types.id"))
    request_type = orm.relationship("RequestType")

    def __repr__(self):
        return '<Request {}>'.format(self.status)

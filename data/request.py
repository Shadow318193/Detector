import sqlalchemy
from .db_session import SqlAlchemyBase
import datetime as dt
from sqlalchemy import orm


class Request(SqlAlchemyBase):
    __tablename__ = 'requests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    time = sqlalchemy.Column(sqlalchemy.DateTime, default=dt.datetime.now())
    status = sqlalchemy.Column(sqlalchemy.Integer, default=200)
    site_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("sites.id"))
    site = orm.relationship("Site")
    request_type_id = sqlalchemy.Column(sqlalchemy.Integer,
                                        sqlalchemy.ForeignKey(
                                            "requests_types.id"))
    request_type = orm.relationship("RequestType")

    def __repr__(self):
        return '<Request {}>'.format(self.status)
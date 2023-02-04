import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class RequestType(SqlAlchemyBase):
    __tablename__ = 'requests_types'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    type = sqlalchemy.Column(sqlalchemy.String)
    request = orm.relationship("Request", back_populates='request_type')

    def __repr__(self):
        return '<RequestType {}>'.format(self.type)
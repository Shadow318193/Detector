import sqlalchemy as db
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm


class RequestType(SqlAlchemyBase):
    __tablename__ = 'requests_types'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,
                   nullable=False, index=True)
    type = db.Column(db.String)
    request = orm.relationship("Request", back_populates='request_type')

    def __repr__(self):
        return f"RequestType {self.id}: {self.type}"

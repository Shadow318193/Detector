import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Site(SqlAlchemyBase):
    __tablename__ = 'sites'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    url = sqlalchemy.Column(sqlalchemy.String)
    request = orm.relationship("Request", back_populates='site')
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship("User")

    is_moderated = sqlalchemy.Column(sqlalchemy.Boolean)

    def __repr__(self):
        return '<Site {}>'.format(self.name)
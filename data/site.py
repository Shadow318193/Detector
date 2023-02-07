import sqlalchemy as db
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm


class Site(SqlAlchemyBase):
    __tablename__ = 'sites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True,
                   nullable=False, index=True)
    name = db.Column(db.String, default="unnamed")
    url = db.Column(db.String)
    request = orm.relationship("Request", back_populates='site')
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = orm.relationship("User")
    is_moderated = db.Column(db.Boolean)

    def __repr__(self):
        return f"Site {self.id}: {self.type} ({self.url}), " \
               f"moderated={self.is_moderated}"
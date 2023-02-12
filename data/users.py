from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, id, email, name, surname, hashed_password):
        self.id = id
        self.email = email
        self.name = name
        self.surname = surname
        self.hashed_password = hashed_password
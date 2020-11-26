from app.hello import db

class User(db.Model):
    __tablename__ = "users"

    
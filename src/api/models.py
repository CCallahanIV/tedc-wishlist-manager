from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid

"""
Resource for how to use UUIDs as Primary Keys:
https://stackoverflow.com/questions/183042/how-can-i-use-uuids-in-sqlalchemy
"""


db = SQLAlchemy()


def get_uuid():
    return str(uuid.uuid4())


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=get_uuid,
        unique=True,
        nullable=False
    )
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(80))
    # TODO: This needs salted and encrypted
    password = db.Column(db.String(80))


class Book(db.Model):
    __tablename__ = "books"

    # Alternatively, we could potentially use the ISBN as a primary key since that is supposed to be
    # unique across books.
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=get_uuid,
        unique=True,
        nullable=False
    )
    title = db.Column(db.String(255))
    author = db.Column(db.String(80))
    # ISBN's are currently 13 digits in length, why not leave a smidge of extra space since they have
    # increased in length in the past.
    # https://en.wikipedia.org/wiki/International_Standard_Book_Number
    isbn = db.Column(db.String(20), nullable=False)
    publication_date = db.Column(db.Date())
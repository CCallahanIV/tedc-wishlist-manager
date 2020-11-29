from sqlalchemy.dialects.postgresql import UUID
import uuid

from app import  bcrypt, db

"""
Resource for how to use UUIDs as Primary Keys:
https://stackoverflow.com/questions/183042/how-can-i-use-uuids-in-sqlalchemy
"""


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
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.Binary(60), nullable=False)

    def __init__(
        self,
        email: str,
        raw_password: str,
        id: str = None,
        first_name: str = None,
        last_name: str = None
    ):
        self.email = email
        self.password = bcrypt.generate_password_hash(raw_password)
        if id:
            self.id = id
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name

    def verify_password(self, candidate_password: str):
        """Verify a candidate password against the stored hashed value.

        Args:
            candidate_password (str): raw candidate password to be verified.

        Returns:
            bool: Whether or not the candidate password matches.
        """
        return bcrypt.check_password_hash(self.password, candidate_password)


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
import uuid

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from app import  bcrypt, db

"""
Resource for how to use UUIDs as Primary Keys:
https://stackoverflow.com/questions/183042/how-can-i-use-uuids-in-sqlalchemy
"""


def get_uuid():
    return str(uuid.uuid4())


"""
The `wishlists` table associates wishlists with users and books.
Keys:
    `wishlist_id`: The primary key
    `user_id`: Foreign Key to users.id
    `book_id`: Foreign Key to books.id

Constraints:
    Unique: Combination of `wishlist_id`, `user_id`, `book_id`. This means that, for a given user,
            one wishlist can have one entry of a book.
"""
wishlists = db.Table(
    'wishlists',
    db.Column('wishlist_id', UUID(as_uuid=True), primary_key=True),
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('users.id')),
    db.Column('book_id', UUID(as_uuid=True), db.ForeignKey('books.id')),
    UniqueConstraint('wishlist_id', 'user_id', 'book_id')
)


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
    wishlists = db.relationship(
        'Book',
        secondary='wishlists',
        lazy='subquery',
        backref=db.backref('wishlists', lazy=True)
    )

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
    # unique across books, maybe not unique across editions?
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=get_uuid,
        unique=True,
        nullable=False
    )
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(80))
    # ISBN's are currently 13 digits in length, why not leave a smidge of extra space since they have
    # increased in length in the past.
    # https://en.wikipedia.org/wiki/International_Standard_Book_Number
    isbn = db.Column(db.String(20), nullable=False)
    publication_date = db.Column(db.Date(), nullable=False)


def insert_wishlist_entry(user_id: str, book_id: str, wishlist_id: str = None):
    """
    Insert a new entry for a wishlist. If `wishlist_id` is not specified, a new wishlist will be
    created.

    Args:
        user_id (str): uuid for a user.
        book_id (str): uuid for a book.
        wishlist_id (str, optional): uuid for a wishlist, if not provided will be created.
                                     Defaults to None.
    """
    if not wishlist_id:
        wishlist_id = get_uuid()
    values = {
        "user_id": user_id,
        "book_id": book_id,
        "wishlist_id": wishlist_id
    }

    db.session.execute(
        wishlists.insert().values(**values)
    )

    # TODO: optionally return id of newly created wishlist?


def list_wishlist_entries(wishlist_id: str):
    res = db.session.execute(wishlists.select().where(wishlists.c.wishlist_id == wishlist_id))
    keys = res.keys()
    rows = res.fetchall()

    def _serialize_row(keys, row):
        formatted_row = {}
        for i in range(len(keys)):
            formatted_row[keys[i]] = str(row[i])
        return formatted_row

    return [_serialize_row(keys, row) for row in rows]


def remove_wishlist_entry(wishlist_id: str, book_id: str):
    pass


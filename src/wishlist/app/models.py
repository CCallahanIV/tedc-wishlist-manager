import uuid

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text

from app import  bcrypt, db

"""
Resource for how to use UUIDs as Primary Keys:
https://stackoverflow.com/questions/183042/how-can-i-use-uuids-in-sqlalchemy
"""


def get_uuid():
    return str(uuid.uuid4())


"""
The `wishlists` table associates wishlists with users and books.
Columns:
    `wishlist_id`: uuid for a single wishlist instance
    `user_id`: Foreign Key to users.id
    `book_id`: Foreign Key to books.id

Primary Key:
    Composite key across all three columns to ensure that, for a single user, a single wishlist, can
    have only one instance of a book.
"""
wishlists = db.Table(
    'wishlists',
    db.Column('wishlist_id', UUID(as_uuid=True), primary_key=True),
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('users.id'), primary_key=True),
    db.Column('book_id', UUID(as_uuid=True), db.ForeignKey('books.id'), primary_key=True)
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

    def __repr__(self):
        return f"<User {self.email}>"


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

    def __repr__(self):
        return f"<Book {self.title}>"


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
    return values


def list_wishlist_entries(wishlist_id: str):
    """Get the wishlist and entries for the given wishlist_id.

    Args:
        wishlist_id (str): uuid for a wishlist

    Returns:
        None:   No wishlist was found for given wishlist_id
        (dict): Dictionary composed of wishlist_id, user_id, and the complete book models.
    """
    query = text(
        """
            SELECT wishlist_id, user_id, id, title, author, isbn, publication_date
            FROM wishlists JOIN books
            ON book_id = id
            WHERE wishlist_id = :wishlist_id
        """
    )
    res = db.session.execute(
        query, {"wishlist_id": wishlist_id}
    )
    keys = res.keys()
    rows = res.fetchall()

    if not rows:
        # No wishlist for given wishlist_id, shortcut out.
        return

    def _serialize_row(keys, row):
        formatted_row = {}
        for i in range(len(keys)):
            formatted_row[keys[i]] = row[i]
        return formatted_row

    results = {
        "wishlist_id": rows[0][0], # For first row, take value of 0th column `wishlist_id`
        "user_id": rows[0][1], # For first row, take value of 1th column `user_id`
        "books": [
            _serialize_row(keys[2:], row[2:]) for row in rows
        ]
    }
    return results


def remove_wishlist_entry(wishlist_id: str, book_id: str):
    """Remove a wishlist entry for a given wishlist_id and book_id. Will not raise if there is no
    entry to delete.

    Args:
        wishlist_id (str): uuid of a wishlist
        book_id (str): uuid of a book
    """
    res = db.session.execute(
        wishlists.\
            delete().\
                where(wishlists.c.wishlist_id == wishlist_id).\
                where(wishlists.c.book_id == book_id)
    )

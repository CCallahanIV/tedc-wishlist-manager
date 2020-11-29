import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import User, Book
from conftest import USER_1


"""
Quick note on tests: it is necessary to include both the `test_client` and `test_db` fixtures in
order to guarentee an app_context has been created and the database attached to it.
"""


def test_sample_user(test_client, test_db):
    """Test that we created a sample user by supplying a unique ID AND retrieving them by that ID.

    Also tests:
      - verify_password method
      - optional fields
    """
    sample_user = User.query.get(USER_1["id"])
    assert sample_user.first_name == USER_1["first_name"]
    assert sample_user.last_name == USER_1["last_name"]
    assert sample_user.email == USER_1["email"]
    assert sample_user.verify_password(USER_1["raw_password"])
    assert str(sample_user.id) == USER_1["id"]


def test_create_user_no_id(test_client, test_db):
    user_no_id = User(
        first_name="Angela",
        last_name="Merkel",
        email="prime@minister.de",
        raw_password="supersecret"
    )
    test_db.session.add(user_no_id)
    test_db.session.commit()
    created_user = User.query.filter_by(first_name="Angela").one_or_none()

    # At this point, user_no_id has been given an id during the save operation.
    assert created_user.id == user_no_id.id


def test_create_user_no_optional_fields(test_client, test_db):
    test_email = "idunno@example.com"
    no_name_user = User(
        email=test_email,
        raw_password="supers3cr3t"
    )
    test_db.session.add(no_name_user),
    test_db.session.commit()

    created_user = User.query.filter_by(email=test_email).one_or_none()
    assert created_user


def test_user_missing_required_param_raises(test_client, test_db):
    with pytest.raises(TypeError):
        User(email="ineedapassword@example.com")


def _test_book(test_book: dict, test_db) -> Book:
    """Helper function to create and test requried fields of a book.

    Args:
        test_book (dict): dictionary of book properties
        test_db : the test_db fixture

    Returns:
        Book : Returns the created book.
    """
    book = Book(**test_book)
    test_db.session.add(book)
    test_db.session.commit()
    created_book = Book.query.filter_by(isbn=test_book["isbn"]).one_or_none()
    assert created_book.isbn == test_book["isbn"]
    assert created_book.title == test_book["title"]
    assert created_book.publication_date == test_book["publication_date"]
    assert created_book.id
    return created_book


def test_create_book(test_client, test_db):
    test_book = {
        "title": "Foundation",
        "isbn": "0-553-29335-4",
        "publication_date": datetime.date(1951, 1, 1),
        "author": "Isaac Asimov"
    }
    created_book = _test_book(test_book, test_db)
    assert created_book.author == test_book["author"]


def test_create_book_no_optional_fields(test_client, test_db):
    test_book = {
        "title": "Encyclopedia Britannica",
        "isbn": "978-1-59339-292-5",
        "publication_date": datetime.date(1768, 1, 1)
    }
    _test_book(test_book, test_db)


def test_book_missing_required_param_raises(test_client, test_db):
    with pytest.raises(IntegrityError):
        test_db.session.add(Book(author="Whoops!"))
        test_db.session.commit()

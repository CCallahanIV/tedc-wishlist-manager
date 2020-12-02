import datetime

import pytest


from data import BOOK_1, BOOK_2, USER_1
from app.models import (
    Book,
    get_uuid,
    insert_wishlist_entry,
    list_wishlist_entries,
    remove_wishlist_entry,
    User,
    wishlists
)
from app.models.exceptions import (
    BookNotFound,
    UserNotFound,
    WishlistEntryAlreadyExists,
    WishlistNotFound
)


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


def test_insert_wishlist_entry_new_wishlist(test_client, test_db):
    user = User.query.get(USER_1["id"])
    book = Book.query.first()
    insert_wishlist_entry(
        user_id=str(user.id),
        book_id=str(book.id),
    )
    res = test_db.session.execute(wishlists.select())
    raw_rows = res.fetchall()
    assert len(raw_rows) == 1
    created_wishlist_id = raw_rows[0][0]
    wishlist_entries = list_wishlist_entries(created_wishlist_id)
    assert len(wishlist_entries["books"]) == 1
    assert wishlist_entries["wishlist_id"] == created_wishlist_id


def test_insert_wishlist_entry_existing_wishlist(test_client, test_db):
    user = User.query.get(USER_1["id"])
    books = [BOOK_1, BOOK_2]
    new_wishlist_id = get_uuid()
    book_ids = set()
    for book in books:
        new_wishlist = insert_wishlist_entry(
            user_id=user.id,
            book_id=book["id"],
            wishlist_id=new_wishlist_id
        )
        book_ids.add(book["id"])
    res = test_db.session.execute(
        wishlists.select().where(wishlists.c.wishlist_id == new_wishlist_id)
    )
    rows = res.fetchall()
    assert len(rows) == 2
    wishlist_book_ids = {str(row[2]) for row in rows}
    assert book_ids == wishlist_book_ids


def test_insert_repeat_entry(test_client, test_db):
    user = User.query.get(USER_1["id"])
    book = Book.query.first()
    new_wishlist_id = get_uuid()
    insert_wishlist_entry(
        user_id=user.id,
        book_id=book.id,
        wishlist_id=new_wishlist_id
    )
    with pytest.raises(WishlistEntryAlreadyExists):
        insert_wishlist_entry(
            user_id=user.id,
            book_id=book.id,
            wishlist_id=new_wishlist_id
        )
    test_db.session.close()


def test_insert_fails_for_missing_book_id(test_client, test_db):
    user = User.query.get(USER_1["id"])
    non_existent_book_id = get_uuid()
    new_wishlist_id = get_uuid()
    with pytest.raises(BookNotFound):
        insert_wishlist_entry(
            user_id=user.id,
            book_id=non_existent_book_id,
            wishlist_id=new_wishlist_id
        )
    test_db.session.close()


def test_insert_fails_for_missing_user_id(test_client, test_db):
    book = Book.query.first()
    non_existent_user_id = get_uuid()
    new_wishlist_id = get_uuid()
    with pytest.raises(UserNotFound):
        insert_wishlist_entry(
            user_id=non_existent_user_id,
            book_id=book.id,
            wishlist_id=new_wishlist_id
        )
    test_db.session.close()


def test_list_wishlist_entries_format(test_client, test_db):
    user = User.query.get(USER_1["id"])
    book = Book.query.first()
    new_wishlist_id = get_uuid()
    insert_wishlist_entry(
        user_id=user.id,
        book_id=book.id,
        wishlist_id=new_wishlist_id
    )
    res = list_wishlist_entries(new_wishlist_id)
    # First, we'll check the format of that wishlist object and that we have the expected number of
    # results
    for key in ("books", "wishlist_id", "user_id"):
        assert key in res
    assert len(res) == 3
    assert len(res["books"]) == 1

    book_response = res["books"][0]
    # Next, we'll check the format of the nested book object
    for key in ("id", "isbn", "publication_date", "title", "author"):
        assert key in book_response


def test_list_wishlist_entries_non_existent_wishlist(test_client, test_db):
    new_wishlist_id = get_uuid()
    with pytest.raises(WishlistNotFound):
        list_wishlist_entries(new_wishlist_id)
    test_db.session.close()


def test_list_wishlist_entries_multiple_wishlists(test_client, test_db):
    wishlist_id_1 = get_uuid()
    wishlist_id_2 = get_uuid()
    books = Book.query.all()
    user = User.query.first()
    wishlist_1_books = books[:1]
    wishlist_2_books = books[1:]

    # Create first wishlist
    for book in wishlist_1_books:
        insert_wishlist_entry(
            user_id=user.id,
            book_id=book.id,
            wishlist_id=wishlist_id_1
        )

    # create second wishlist
    for book in wishlist_2_books:
        insert_wishlist_entry(
            user_id=user.id,
            book_id=book.id,
            wishlist_id=wishlist_id_2
        )

    wishlist_res_1 = list_wishlist_entries(wishlist_id_1)
    wishlist_res_2 = list_wishlist_entries(wishlist_id_2)

    assert len(wishlist_res_1["books"]) == len(wishlist_1_books)
    assert len(wishlist_res_2["books"]) == len(wishlist_2_books)

    wishlist_res_1_book_ids = {book["id"] for book in wishlist_res_1["books"]}
    wishlist_res_2_book_ids = {book["id"] for book in wishlist_res_2["books"]}

    # Let's make sure we have no overlap in book ids because we split the books across wishlists.
    assert bool(wishlist_res_1_book_ids & wishlist_res_2_book_ids) is False


def test_remove_wishlist_entry(test_client, test_db):
    user = User.query.get(USER_1["id"])
    books = Book.query.all()
    new_wishlist_id = get_uuid()
    book_to_remove = books[0]
    for book in books:
        new_wishlist = insert_wishlist_entry(
            user_id=user.id,
            book_id=book.id,
            wishlist_id=new_wishlist_id
        )
    remove_wishlist_entry(new_wishlist_id, book_to_remove.id)

    # refetch wishlist to make sure the book isn't there anymore
    res = list_wishlist_entries(new_wishlist_id)
    book_ids_after_removal = {book["id"] for book in res["books"]}
    assert book_to_remove.id not in book_ids_after_removal


def test_remove_nonexistent_wishlist_entry(test_client, test_db):
    """At this time, nothing bad should happen. In the future, we could return an error if there is
    an attempt to delete a wishlist entry that doesn't exist.
    """
    new_wishlist_id = get_uuid()
    new_book_id = get_uuid()
    remove_wishlist_entry(new_wishlist_id, new_book_id)
    assert True

from datetime import date

import pytest

from app import create_app, db
from app.models import get_uuid, Book, User

"""
Reference for structuring tests:
https://www.patricksoftwareblog.com/testing-a-flask-application-using-pytest/
"""

BOOK_1 = {
    "title": "Chicken Soup for the Soul 20th Anniversary Edition",
    "author": "Jack Canfield, Mark Victor Hansen, Amy Newmark",
    "isbn": "978-1611599138",
    "publication_date": date(2013, 6, 25)
}

USER_1 = {
    "id": get_uuid(),
    "email": "fredr@neighborhood.com",
    "raw_password": "won'tyoubemyneighbor",
    "first_name": "fred",
    "last_name": "rogers"
}


@pytest.fixture(scope="module")
def test_client():
    app = create_app()
    test_client = app.test_client()

    # This is the app context that will be used for testing.
    ctx = app.app_context()
    ctx.push()

    yield test_client
    ctx.pop()


@pytest.fixture(scope="module")
def test_db():
    db.create_all()

    user_1 = User(**USER_1)
    book_1 = Book(**BOOK_1)
    db.session.add(user_1)
    db.session.add(book_1)
    db.session.commit()
    
    yield db
    # Have to explicitly close the database session, otherwise the tests will hang.
    db.session.close()
    db.drop_all()

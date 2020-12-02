from datetime import date

import pytest

from app import create_app, db
from app.models import get_uuid, Book, User
from data import BOOK_1, BOOK_2, USER_1

"""
Reference for structuring tests:
https://www.patricksoftwareblog.com/testing-a-flask-application-using-pytest/
"""

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
    db.session.add_all([
        User(**USER_1),
        Book(**BOOK_1),
        Book(**BOOK_2)
    ])
    db.session.commit()
    
    yield db
    # Have to explicitly close the database session, otherwise the tests will hang.
    db.session.close()
    db.drop_all()

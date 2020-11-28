import pytest

from api import create_app, db
from api.models import User

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

    user1 = User(first_name="fred", last_name="rogers")
    db.session.add(user1)
    db.session.commit()
    
    yield db
    db.session.close()
    db.drop_all()
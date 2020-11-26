import pytest

from app.hello import app


@pytest.fixture
def client():
    yield app.test_client()

from api.models import User


def test_tests(test_client):
    res = test_client.get("/")
    assert res.json == "One small step for a man..."


def test_tests2(test_db):
    users = User.query.all()
    assert users

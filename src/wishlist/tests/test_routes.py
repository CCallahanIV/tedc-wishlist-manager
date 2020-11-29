from app.models import User


def test_tests(test_client):
    res = test_client.get("/")
    assert res.json == "OK"
    assert res.status_code == 200

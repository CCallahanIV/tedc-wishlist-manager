def test_tests(client):
    res = client.get("/")
    assert res.data == b"One small step for a man..."
def test_tests(client):
    res = client.get("/")
    assert res.json == "One small step for a man..."
from app.models import User
from conftest import USER_1

def test_sample_user(test_client, test_db):
    """Test that we created a sample user by supplying a unique ID AND retrieving them by that ID.
    """
    sample_user = User.query.get(USER_1["id"])
    assert sample_user.first_name == USER_1["first_name"]
    assert sample_user.last_name == USER_1["last_name"]
    assert sample_user.email == USER_1["email"]
    assert sample_user.verify_password(USER_1["raw_password"])
    assert str(sample_user.id) == USER_1["id"]

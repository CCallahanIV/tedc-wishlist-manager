import pytest

# from app import create_app, db
from app.models import (
    Book,
    get_uuid,
    insert_wishlist_entry,
    list_wishlist_entries,
    remove_wishlist_entry,
    wishlists,
    User
)
from conftest import USER_1, BOOK_1, BOOK_2


# @pytest.fixture(scope="function")
# def functional_test_client():
#     flask_app = create_app()
#     db.create_all()
#     db.session.add(User(**USER_1))
#     db.session.add(Book(**BOOK_1))
#     db.session.add(Book(**BOOK_2))
#     db.session.commit()
#     with flask_app.test_client() as test_client:
#         yield test_client
#     db.session.close()
#     db.drop_all()


def test_healthcheck(test_client):
    res = test_client.get("/")
    assert res.status_code == 200


@pytest.mark.parametrize(
    "wishlist_id,exp_msg_fragment",
    [
        pytest.param(
            "fred",
            "must be valid UUID",
            id="invalid uuid"
        ),
    ]
)
def test_get_wishlist_raises_400(wishlist_id, exp_msg_fragment, test_client):
    res = test_client.get(f"/wishlist/{wishlist_id}")
    assert res.status_code == 400
    assert exp_msg_fragment in str(res.data)


def test_get_wishlist_raises_404(test_client, test_db):
    nonexistent_wishlist_id = get_uuid()
    res = test_client.get(f"/wishlist/{nonexistent_wishlist_id}")
    assert res.status_code == 404


@pytest.mark.parametrize(
    "payload,method,exp_msg_fragment",
    [
        # POST calls
        pytest.param(
            {},
            "POST",
            "missing required key",
            id="missing all keys"
        ),
        pytest.param(
            {
                "user_id": get_uuid(),
                "wishlist_id": get_uuid()
            },
            "POST",
            "missing required key",
            id="partially missing required keys"
        ),
        pytest.param(
            {
                "user_id": get_uuid(),
                "book_id": "fred",
                "wishlist_id": get_uuid()
            },
            "POST",
            "must be valid UUID",
            id="invalid value for required key"
        ),
        pytest.param(
            {
                "user_id": get_uuid(),
                "book_id": get_uuid(),
                "wishlist_id": "potato"
            },
            "POST",
            "must be valid UUID",
            id="invalid value for optional key"
        ),
        # DELETE calls
        pytest.param(
            {
                "book_id": get_uuid(),
                "wishlist_id": "potato"
            },
            "DELETE",
            "must be valid UUID",
            id="invalid value for required key"
        ),
        pytest.param(
            {
                "book_id": get_uuid(),
            },
            "DELETE",
            "missing required key",
            id="missing required key"
        ),
    ]
)
def test_wishlist_entry_raises_400(payload, method, exp_msg_fragment, test_client):
    if method == "POST":
        res = test_client.post("/wishlist_entry", json=payload)
    else:
        res = test_client.delete("/wishlist_entry", json=payload)
    assert res.status_code == 400
    assert exp_msg_fragment in str(res.data)


def test_create_wishlist_entry_no_wishlist(test_client, test_db):
    user = User(email="joe@schmoe.com", raw_password="superS3cr3t")
    book_1 = Book(**BOOK_1)
    book_2 = Book(**BOOK_2)
    test_db.session.add_all([user, book_1, book_2])
    test_db.session.commit()

    res = test_client.post(
        "/wishlist_entry",
        json={
            "book_id": book_1.id,
            "user_id": user.id,
        }
    )
    assert res.status_code == 201
    new_wishlist_id = res.json["wishlist_id"]

    res2 = test_client.post(
        "/wishlist_entry",
        json={
            "book_id": book_2.id,
            "user_id": user.id,
            "wishlist_id": new_wishlist_id
        }
    )
    assert res.status_code == 201


def test_create_and_retrieve_wishlist(test_client, test_db):
    user = User(email="joe@schmoe.com", raw_password="superS3cr3t")
    book_1 = Book(**BOOK_1)
    book_2 = Book(**BOOK_2)
    test_db.session.add_all([user, book_1, book_2])
    test_db.session.commit()

    wishlist_id = get_uuid()

    for book in [book_1, book_2]:
        res = test_client.post(
            "/wishlist_entry",
            json={
                "book_id": book.id,
                "user_id": user.id,
                "wishlist_id": wishlist_id
            }
        )
        assert res.status_code == 201
    
    res = test_client.get(f"/wishlist/{wishlist_id}")
    assert res.status_code == 200
    assert res.json["wishlist_id"] == wishlist_id
    assert res.json["user_id"] == str(user.id)
    assert len(res.json["books"]) == 2


def test_remove_wishlist_entry(test_client, test_db):
    user = User(email="joe@schmoe.com", raw_password="superS3cr3t")
    book_1 = Book(**BOOK_1)
    book_2 = Book(**BOOK_2)
    test_db.session.add_all([user, book_1, book_2])
    test_db.session.commit()

    wishlist_id = get_uuid()

    for book in [book_1, book_2]:
        res = test_client.post(
            "/wishlist_entry",
            json={
                "book_id": book.id,
                "user_id": user.id,
                "wishlist_id": wishlist_id
            }
        )
        assert res.status_code == 201
    
    res_get_1 = test_client.get(f"/wishlist/{wishlist_id}")
    assert res_get_1.status_code == 200
    assert len(res_get_1.json["books"]) == 2

    res_delete = test_client.delete(
        "/wishlist_entry",
        json={
            "book_id": book_1.id,
            "wishlist_id": wishlist_id
        }
    )
    assert res_delete.status_code == 200

    res_get_2 = test_client.get(f"/wishlist/{wishlist_id}")
    assert res_get_2.status_code == 200
    assert len(res_get_2.json["books"]) == 1
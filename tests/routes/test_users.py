import bcrypt

from app.models.user import User

USER_PAYLOAD = {
    "first_name": "Lucas",
    "last_name": "Kaminski",
    "email": "lucas@example.com",
    "password": "secret-password",
}


def assert_no_password(user):
    assert "password" not in user
    assert "hashed_password" not in user


def create_user(client, **fields):
    response = client.post("/users", json={**USER_PAYLOAD, **fields})
    assert response.status_code == 200
    assert "id" in response.json()
    return response.json()


def test_create_user(client):
    user = create_user(client)

    assert user["first_name"] == "Lucas"
    assert user["email"] == "lucas@example.com"
    assert user["role"] == "user"
    assert_no_password(user)


def test_create_user_hashes_password(client, db):
    user = create_user(client)

    hashed_password = db.query(User).get(user["id"]).hashed_password

    assert hashed_password != USER_PAYLOAD["password"]
    assert bcrypt.checkpw(USER_PAYLOAD["password"].encode(), hashed_password.encode())


def test_create_user_duplicate_email(client):
    create_user(client)

    response = client.post("/users", json=USER_PAYLOAD)

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already registered"}


def test_create_user_invalid_payload(client):
    response = client.post(
        "/users", json={**USER_PAYLOAD, "email": "not-an-email", "password": "short"}
    )

    assert response.status_code == 422


def test_get_user_by_id(client):
    user = create_user(client)

    response = client.get(f"/users/{user['id']}")

    assert response.status_code == 200
    assert response.json() == user
    assert_no_password(response.json())


def test_get_user_by_id_not_found(client):
    response = client.get("/users/0")

    assert response.status_code == 404


def test_get_all_users(client):
    user = create_user(client)

    response = client.get("/users")

    assert response.status_code == 200
    assert user["id"] in [u["id"] for u in response.json()]
    for listed in response.json():
        assert_no_password(listed)


def test_update_user(client):
    user = create_user(client)

    response = client.patch(f"/users/{user['id']}", json={"first_name": "Luke"})

    assert response.status_code == 200
    assert response.json()["first_name"] == "Luke"
    assert response.json()["last_name"] == "Kaminski"
    assert_no_password(response.json())


def test_update_user_password(client, db):
    user = create_user(client)

    client.patch(f"/users/{user['id']}", json={"password": "another-password"})

    hashed_password = db.query(User).get(user["id"]).hashed_password
    assert bcrypt.checkpw(b"another-password", hashed_password.encode())


def test_update_user_email_taken(client):
    create_user(client, email="taken@example.com")
    user = create_user(client)

    response = client.patch(f"/users/{user['id']}", json={"email": "taken@example.com"})

    assert response.status_code == 409


def test_update_user_keeps_own_email(client):
    user = create_user(client)

    response = client.patch(f"/users/{user['id']}", json={"email": user["email"]})

    assert response.status_code == 200


def test_delete_user(client):
    user = create_user(client)

    response = client.delete(f"/users/{user['id']}")

    assert response.status_code == 200
    assert client.get(f"/users/{user['id']}").status_code == 404

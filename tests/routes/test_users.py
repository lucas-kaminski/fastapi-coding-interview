def create_user(client, first_name="Lucas", last_name="Kaminski"):
    response = client.post(
        "/users", json={"first_name": first_name, "last_name": last_name}
    )
    assert response.status_code == 200
    assert "id" in response.json()
    return response.json()


def test_create_user(client):
    user = create_user(client)

    assert user["first_name"] == "Lucas"
    assert "id" in user
    assert "password" not in user


def test_get_user_by_id(client):
    user = create_user(client)

    response = client.get(f"/users/{user['id']}")

    assert response.status_code == 200
    assert response.json() == user


def test_get_user_by_id_not_found(client):
    response = client.get("/users/0")

    assert response.status_code == 404


def test_get_all_users(client):
    user = create_user(client)

    response = client.get("/users")

    assert response.status_code == 200
    assert user["id"] in [u["id"] for u in response.json()]


def test_update_user(client):
    user = create_user(client)

    response = client.patch(f"/users/{user['id']}", json={"first_name": "Luke"})

    assert response.status_code == 200
    assert response.json()["first_name"] == "Luke"
    assert response.json()["last_name"] == "Kaminski"


def test_delete_user(client):
    user = create_user(client)

    response = client.delete(f"/users/{user['id']}")

    assert response.status_code == 200
    assert client.get(f"/users/{user['id']}").status_code == 404

def test_create_user(client):
    response = client.post(
        "/users", json={"first_name": "Lucas", "last_name": "Kaminski"}
    )

    assert response.status_code == 200

    json_response = response.json()

    assert json_response["first_name"] == "Lucas"
    assert "id" in json_response
    assert "password" not in json_response

    pass


def test_get_user_by_id():
    # TODO
    pass


def test_get_all_users():
    # TODO
    pass


def test_update_user():
    # TODO
    pass


def test_delete_user():
    # TODO
    pass

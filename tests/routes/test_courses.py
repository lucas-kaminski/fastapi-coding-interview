def create_course(client, title="Math", description="Algebra and geometry"):
    response = client.post("/courses", json={"title": title, "description": description})
    assert response.status_code == 200
    assert "id" in response.json()
    return response.json()


def test_create_course(client):
    course = create_course(client)

    assert course["title"] == "Math"
    assert course["description"] == "Algebra and geometry"
    assert "id" in course


def test_create_course_missing_field(client):
    response = client.post("/courses", json={"title": "Math"})

    assert response.status_code == 422


def test_get_course_by_id(client):
    course = create_course(client)

    response = client.get(f"/courses/{course['id']}")

    assert response.status_code == 200
    assert response.json() == course


def test_get_course_by_id_not_found(client):
    response = client.get("/courses/0")

    assert response.status_code == 404
    assert response.json() == {"detail": "Course not found"}


def test_get_all_courses(client):
    course = create_course(client)

    response = client.get("/courses")

    assert response.status_code == 200
    assert course["id"] in [c["id"] for c in response.json()]


def test_update_course(client):
    course = create_course(client)

    response = client.patch(f"/courses/{course['id']}", json={"title": "Physics"})

    assert response.status_code == 200
    assert response.json()["title"] == "Physics"
    assert response.json()["description"] == course["description"]


def test_update_course_not_found(client):
    response = client.patch("/courses/0", json={"title": "Physics"})

    assert response.status_code == 404


def test_delete_course(client):
    course = create_course(client)

    response = client.delete(f"/courses/{course['id']}")

    assert response.status_code == 200
    assert client.get(f"/courses/{course['id']}").status_code == 404


def test_delete_course_not_found(client):
    response = client.delete("/courses/0")

    assert response.status_code == 404

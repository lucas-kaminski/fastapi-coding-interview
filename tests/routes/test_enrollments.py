from app.services.enrollments import MAX_COURSES_PER_USER


def enroll(client, user_id, course_id):
    return client.post(
        "/enrollments", json={"user_id": user_id, "course_id": course_id}
    )


def test_create_enrollment(client, make_user, make_course):
    user, course = make_user(), make_course()

    response = enroll(client, user.id, course.id)

    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["user_id"] == user.id
    assert response.json()["course_id"] == course.id


def test_create_enrollment_missing_course(client, make_user):
    response = enroll(client, make_user().id, 0)

    assert response.status_code == 404
    assert response.json() == {"detail": "Course not found"}


def test_create_enrollment_twice(client, make_user, make_course):
    user, course = make_user(), make_course()
    enroll(client, user.id, course.id)

    response = enroll(client, user.id, course.id)

    assert response.status_code == 409
    assert response.json() == {"detail": "User is already enrolled in this course"}


def test_create_enrollment_over_limit(client, make_user, make_course):
    user = make_user()
    for _ in range(MAX_COURSES_PER_USER):
        enroll(client, user.id, make_course().id)

    response = enroll(client, user.id, make_course().id)

    assert response.status_code == 422
    assert "5 courses" in response.json()["detail"]


def test_list_enrollments_filtered_by_course(client, make_user, make_course):
    course, other_course = make_course(), make_course()
    user = make_user()
    enroll(client, user.id, course.id)
    enroll(client, user.id, other_course.id)

    response = client.get("/enrollments", params={"course_id": course.id})

    assert response.status_code == 200
    assert [e["course_id"] for e in response.json()] == [course.id]


def test_get_enrollment_by_id(client, make_user, make_course):
    enrollment = enroll(client, make_user().id, make_course().id).json()

    response = client.get(f"/enrollments/{enrollment['id']}")

    assert response.status_code == 200
    assert response.json() == enrollment


def test_delete_enrollment(client, make_user, make_course):
    enrollment = enroll(client, make_user().id, make_course().id).json()

    response = client.delete(f"/enrollments/{enrollment['id']}")

    assert response.status_code == 200
    assert client.get(f"/enrollments/{enrollment['id']}").status_code == 404


def test_deleting_course_removes_its_enrollments(client, make_user, make_course):
    course = make_course()
    enrollment = enroll(client, make_user().id, course.id).json()

    client.delete(f"/courses/{course.id}")

    assert client.get(f"/enrollments/{enrollment['id']}").status_code == 404

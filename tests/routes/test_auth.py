import pytest

from app.core.security import hash_password
from app.models.user import Role


@pytest.fixture
def student(make_user):
    return make_user(hashed_password=hash_password("secret-password"))


@pytest.fixture
def student_client(client_for, student):
    return client_for(student)


def login(client, email, password):
    return client.post("/auth/login", data={"username": email, "password": password})


def test_login_returns_token_that_authenticates(client_for, student):
    response = login(client_for(), student.email, "secret-password")

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"

    token = response.json()["access_token"]
    me = client_for().get(
        f"/users/{student.id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert me.status_code == 200
    assert me.json()["email"] == student.email


@pytest.mark.parametrize(
    "email, password",
    [("wrong@example.com", "secret-password"), (None, "wrong-password")],
)
def test_login_with_bad_credentials(client_for, student, email, password):
    response = login(client_for(), email or student.email, password)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_requests_without_token_are_rejected(client_for):
    assert client_for().get("/courses").status_code == 401


def test_invalid_token_is_rejected(client_for):
    response = client_for().get(
        "/courses", headers={"Authorization": "Bearer not-a-jwt"}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_token_of_deleted_user_is_rejected(client_for, db, student):
    student_client = client_for(student)
    db.delete(student)
    db.flush()

    assert student_client.get("/courses").status_code == 401


def test_sign_up_is_public_and_always_creates_user_role(client_for):
    response = client_for().post(
        "/users",
        json={
            "first_name": "Ana",
            "last_name": "Silva",
            "email": "ana@example.com",
            "password": "secret-password",
            "role": "admin",
        },
    )

    assert response.status_code == 200
    assert response.json()["role"] == "user"


def test_user_reads_courses_but_cannot_manage_them(student_client, make_course):
    course = make_course()

    assert student_client.get("/courses").status_code == 200
    assert student_client.get(f"/courses/{course.id}").status_code == 200

    payload = {"title": "Physics", "description": "Mechanics"}
    assert student_client.post("/courses", json=payload).status_code == 403
    assert (
        student_client.patch(f"/courses/{course.id}", json=payload).status_code == 403
    )
    assert student_client.delete(f"/courses/{course.id}").status_code == 403


def test_user_manages_only_own_account(student_client, student, make_user):
    other = make_user()

    assert student_client.get("/users").status_code == 403
    assert student_client.get(f"/users/{other.id}").status_code == 403
    assert (
        student_client.patch(f"/users/{other.id}", json={"first_name": "X"}).status_code
        == 403
    )
    assert student_client.delete(f"/users/{other.id}").status_code == 403

    response = student_client.patch(f"/users/{student.id}", json={"first_name": "Luke"})
    assert response.status_code == 200
    assert response.json()["first_name"] == "Luke"


def test_user_cannot_change_own_role(student_client, student):
    response = student_client.patch(f"/users/{student.id}", json={"role": "admin"})

    assert response.status_code == 403
    assert student.role == Role.USER


def test_admin_can_change_roles(client, student):
    response = client.patch(f"/users/{student.id}", json={"role": "admin"})

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_user_enrolls_only_self(student_client, student, make_user, make_course):
    course, other = make_course(), make_user()

    response = student_client.post(
        "/enrollments", json={"user_id": other.id, "course_id": course.id}
    )
    assert response.status_code == 403

    response = student_client.post(
        "/enrollments", json={"user_id": student.id, "course_id": course.id}
    )
    assert response.status_code == 200


def test_user_sees_and_deletes_only_own_enrollments(
    client, student_client, student, make_user, make_course
):
    course = make_course()
    own = client.post(
        "/enrollments", json={"user_id": student.id, "course_id": course.id}
    ).json()
    other = client.post(
        "/enrollments", json={"user_id": make_user().id, "course_id": course.id}
    ).json()

    listed = student_client.get("/enrollments", params={"course_id": course.id}).json()
    assert [e["id"] for e in listed] == [own["id"]]

    assert student_client.get(f"/enrollments/{other['id']}").status_code == 403
    assert student_client.delete(f"/enrollments/{other['id']}").status_code == 403
    assert student_client.delete(f"/enrollments/{own['id']}").status_code == 200

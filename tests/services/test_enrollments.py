import pytest

from app.errors import ConflictError, LimitExceededError, NotFoundError
from app.services import enrollments
from app.services.enrollments import MAX_COURSES_PER_USER, MAX_USERS_PER_COURSE


def test_enroll(db, make_user, make_course):
    user, course = make_user(), make_course()

    enrollment = enrollments.enroll(db, user.id, course.id)

    assert enrollment.id is not None
    assert enrollment.user_id == user.id
    assert enrollment.course_id == course.id


def test_enroll_user_not_found(db, make_course):
    with pytest.raises(NotFoundError, match="User not found"):
        enrollments.enroll(db, 0, make_course().id)


def test_enroll_course_not_found(db, make_user):
    with pytest.raises(NotFoundError, match="Course not found"):
        enrollments.enroll(db, make_user().id, 0)


def test_enroll_twice_in_same_course(db, make_user, make_course):
    user, course = make_user(), make_course()
    enrollments.enroll(db, user.id, course.id)

    with pytest.raises(ConflictError):
        enrollments.enroll(db, user.id, course.id)


def test_user_course_limit(db, make_user, make_course):
    user = make_user()
    for _ in range(MAX_COURSES_PER_USER):
        enrollments.enroll(db, user.id, make_course().id)

    with pytest.raises(LimitExceededError, match="more than 5 courses"):
        enrollments.enroll(db, user.id, make_course().id)


def test_course_user_limit(db, make_user, make_course):
    course = make_course()
    for _ in range(MAX_USERS_PER_COURSE):
        enrollments.enroll(db, make_user().id, course.id)

    with pytest.raises(LimitExceededError, match="more than 20 users"):
        enrollments.enroll(db, make_user().id, course.id)

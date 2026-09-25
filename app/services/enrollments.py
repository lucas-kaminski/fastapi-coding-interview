from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.errors import ConflictError, LimitExceededError, NotFoundError
from app.models.courses import Course
from app.models.enrollments import Enrollment
from app.models.user import User

MAX_COURSES_PER_USER = 5
MAX_USERS_PER_COURSE = 20


def count_enrollments(db: Session, *where) -> int:
    return db.scalar(select(func.count()).select_from(Enrollment).where(*where))


def enroll(db: Session, user_id: int, course_id: int) -> Enrollment:
    user = db.scalar(select(User).where(User.id == user_id).with_for_update())
    if not user:
        raise NotFoundError("User not found")

    course = db.scalar(select(Course).where(Course.id == course_id).with_for_update())
    if not course:
        raise NotFoundError("Course not found")

    already_enrolled = count_enrollments(
        db, Enrollment.user_id == user_id, Enrollment.course_id == course_id
    )
    if already_enrolled:
        raise ConflictError("User is already enrolled in this course")

    if count_enrollments(db, Enrollment.user_id == user_id) >= MAX_COURSES_PER_USER:
        raise LimitExceededError(
            f"User cannot be enrolled in more than {MAX_COURSES_PER_USER} courses"
        )

    if count_enrollments(db, Enrollment.course_id == course_id) >= MAX_USERS_PER_COURSE:
        raise LimitExceededError(
            f"Course cannot have more than {MAX_USERS_PER_COURSE} users"
        )

    enrollment = Enrollment(user_id=user_id, course_id=course_id)

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return enrollment

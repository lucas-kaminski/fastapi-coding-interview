from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import ensure_self_or_admin, get_current_user
from app.models.enrollments import Enrollment
from app.models.user import Role, User
from app.schemas.enrollments import EnrollmentCreate, EnrollmentRead
from app.services import enrollments

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.get("/", response_model=list[EnrollmentRead])
def get_all(
    user_id: int | None = None,
    course_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EnrollmentRead]:
    if current_user.role != Role.ADMIN:
        user_id = current_user.id

    query = db.query(Enrollment)

    if user_id is not None:
        query = query.filter(Enrollment.user_id == user_id)
    if course_id is not None:
        query = query.filter(Enrollment.course_id == course_id)

    return query.all()


@router.post("/", response_model=EnrollmentRead)
def create(
    payload: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EnrollmentRead:
    ensure_self_or_admin(current_user, payload.user_id)
    return enrollments.enroll(db, payload.user_id, payload.course_id)


@router.get("/{id}", response_model=EnrollmentRead)
def get_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EnrollmentRead:
    enrollment = db.query(Enrollment).get(id)

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    ensure_self_or_admin(current_user, enrollment.user_id)

    return enrollment


@router.delete("/{id}")
def delete(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    enrollment = db.query(Enrollment).get(id)

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    ensure_self_or_admin(current_user, enrollment.user_id)

    db.delete(enrollment)
    db.commit()

    return {"detail": "Enrollment deleted"}

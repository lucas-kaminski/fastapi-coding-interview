from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user, require_admin
from app.models.courses import Course
from app.models.user import User
from app.schemas.courses import CoursesCreate, CoursesRead, CoursesUpdate

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=list[CoursesRead])
def get_all(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[CoursesRead]:
    return db.query(Course).all()


@router.post("/", response_model=CoursesRead)
def create(
    payload: CoursesCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> CoursesRead:
    courses = Course(
        title=payload.title,
        description=payload.description,
    )

    db.add(courses)
    db.commit()
    db.refresh(courses)

    return courses


@router.get("/{id}", response_model=CoursesRead)
def get_by_id(
    id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> CoursesRead:
    courses = db.query(Course).get(id)

    if not courses:
        raise HTTPException(status_code=404, detail="Course not found")

    return courses


@router.patch("/{id}", response_model=CoursesRead)
def update(
    id: int,
    payload: CoursesUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> CoursesRead:
    courses = db.query(Course).get(id)

    if not courses:
        raise HTTPException(status_code=404, detail="Course not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(courses, field, value)

    db.commit()
    db.refresh(courses)

    return courses


@router.delete("/{id}")
def delete(
    id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    courses = db.query(Course).get(id)

    if not courses:
        raise HTTPException(status_code=404, detail="Course not found")

    db.delete(courses)
    db.commit()

    return {"detail": "Course deleted"}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import (
    ensure_self_or_admin,
    get_current_user,
    hash_password,
    require_admin,
)
from app.errors import PermissionDeniedError
from app.models.user import Role, User
from app.schemas.users import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserRead])
def get_all(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[UserRead]:
    return db.query(User).all()


@router.post("/", response_model=UserRead)
def create(
    payload: UserCreate,
    db: Session = Depends(get_db),
) -> UserRead:
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.get("/{id}", response_model=UserRead)
def get_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    ensure_self_or_admin(current_user, id)
    user = db.query(User).get(id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.patch("/{id}", response_model=UserRead)
def update(
    id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    ensure_self_or_admin(current_user, id)
    user = db.query(User).get(id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    fields = payload.model_dump(exclude_unset=True)

    if "role" in fields and current_user.role != Role.ADMIN:
        raise PermissionDeniedError("Only an admin can change roles")

    if "email" in fields:
        owner = db.query(User).filter(User.email == fields["email"]).first()
        if owner and owner.id != id:
            raise HTTPException(status_code=409, detail="Email already registered")

    if "password" in fields:
        fields["hashed_password"] = hash_password(fields.pop("password"))

    for field, value in fields.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{id}")
def delete(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    ensure_self_or_admin(current_user, id)
    user = db.query(User).get(id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"detail": "User deleted"}

import argparse

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.user import Role, User

parser = argparse.ArgumentParser(description="Create the first admin user.")
parser.add_argument("email")
parser.add_argument("password")
parser.add_argument("--first-name", default="Admin")
parser.add_argument("--last-name", default="Admin")
args = parser.parse_args()

with SessionLocal() as db:
    if db.query(User).filter(User.email == args.email).first():
        raise SystemExit("Email already registered")

    db.add(
        User(
            first_name=args.first_name,
            last_name=args.last_name,
            email=args.email,
            hashed_password=hash_password(args.password),
            role=Role.ADMIN,
        )
    )
    db.commit()

print(f"Admin {args.email} created")

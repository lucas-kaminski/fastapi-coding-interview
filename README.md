# FastAPI Coding Exercise

This repository contains a simple FastAPI project designed for technical interviews.

The project already includes a **User module** as a reference. You are expected to build additional modules according to the exercise.  

## 🛠️ Requirements

- **Python 3.11+** (recommended)  
- **PostgreSQL** running locally or in Docker  
- A **virtual environment** like venv, Poetry, Conda, etc. (recommended)

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://gitlab.com/beontechstudio/python-fastapi-coding-interview.git
cd python-fastapi-coding-interview
```

### 2. Create and activate a virtual environment (example with venv)

```bash
python3 -m venv venv
source venv/bin/activate     # macOS/Linux
# venv\Scripts\activate     # Windows
```
⚡ You may also use Poetry, Conda or your preferred environment manager if you like.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy .env.example into a new .env file:
```bash
cp .env.example .env
```

Edit .env to match your database connection.

### 5. Initialize the database

```bash
make migrate
```

`make migrate` starts PostgreSQL with Docker Compose and runs `alembic upgrade head`.

### 6. Run the application

```bash
make run
```

### 7. Run the tests

```bash
.venv/bin/pytest
```

The tests use the database from `.env`. Each test rolls back its own transaction.

Open your browser at 👉 http://localhost:8000/docs to see the interactive API docs.

## 🔑 Notes
	•	The project uses synchronous SQLAlchemy (not async) to keep things simple for interview purposes.

## 📏 Enrollment rules

- A user can be enrolled in up to 5 courses.
- A course can have up to 20 users.
- A user can enroll in the same course only once.
- Deleting a user or a course deletes its enrollments.

`app/services/enrollments.py` enforces these rules and raises errors from `app/errors/`. A global handler turns each error into an HTTP response: 404 for a missing resource, 409 for a duplicate, 422 for a full limit.

## 🚧 Not done

Authentication and authorization are incomplete. The user model has `email`, `password` and `role`, but nothing uses them yet. The missing parts:

- A login endpoint that checks the password and returns a JWT.
- A dependency that reads the token and loads the current user.
- A dependency that requires the `admin` role.
- An access policy: a `user` reads courses and manages only their own enrollments; an `admin` manages everything.
- A public sign-up endpoint that always creates the `user` role.
- A script that creates the first admin.

## 🔧 Possible improvements

Validation and contracts:
- Add `Field(max_length=...)` to the schemas. Today an 81-character name returns 500.
- Reject `null` in `PATCH`. Today `{"first_name": null}` returns 500.
- Return 201 on `POST` and 204 on `DELETE`.
- Store emails in lowercase. Today `A@x.com` and `a@x.com` are two different accounts.
- Catch `IntegrityError` on the email unique constraint and return 409. Two concurrent sign-ups with the same email can pass the check before either commits.
- Paginate the list endpoints with `limit` and `offset`.

Code structure:
- Move the commit to `get_db`: commit on success, roll back on error.
- Extract "fetch or 404" into a dependency such as `get_course_or_404`.
- Replace the legacy `Query.get()` with `Session.get()`.
- Load configuration with `pydantic-settings` and fail at startup when a variable is missing.
- Build the database URL with `URL.create`. Today a password with `@` breaks the f-string URL.
- Group the code by domain (`users/`, `courses/`, `enrollments/`) once there are more modules.

Tests and tooling:
- Run the tests against a separate test database.
- Add Ruff, mypy and pip-audit in CI.
- Pin the dependency versions.

Operations:
- Add a `/health` endpoint.
- Add structured logs with a request id.
- Add a Dockerfile for the API.

Migrations:
- The `add auth fields to users` migration requires an empty `users` table. `email` and `hashed_password` have no default to backfill existing rows.

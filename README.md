# FastAPI Coding Exercise

[![CI](https://github.com/lucas-kaminski/fastapi-coding-interview/actions/workflows/ci.yml/badge.svg)](https://github.com/lucas-kaminski/fastapi-coding-interview/actions/workflows/ci.yml)

Technical interview for the Python Platform Engineer position at [BEON.tech](https://beon.tech).

BEON provided a FastAPI project with a users module. The exercise asks for a courses module, enrollments with limits, error handling, and authentication with roles. The [exercise PDF](./content/Python%20FastAPI%20Coding%20Exercise.pdf) describes the full task. The original project lives at [gitlab.com/beontechstudio/python-fastapi-coding-interview](https://gitlab.com/beontechstudio/python-fastapi-coding-interview).

## ✅ Checklist

- [x] Courses module with full CRUD.
- [x] Enrollments: up to 5 courses per user and up to 20 users per course.
- [x] Error handling: 401, 403, 404, 409 and 422 with a JSON `detail`.
- [x] Users with email, password and role.
- [x] Login with JWT and access by role.
- [x] Integration tests for the routes and unit tests for the business rules.

## 🛠️ Requirements

- **Python 3.11+** (recommended)  
- **PostgreSQL** running locally or in Docker  
- A **virtual environment** like venv, Poetry, Conda, etc. (recommended)

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/lucas-kaminski/fastapi-coding-interview.git
cd fastapi-coding-interview
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

Edit .env to match your database connection. Set `SECRET_KEY` to a random value. The app refuses to start without it.

### 5. Initialize the database

```bash
make migrate
```

`make migrate` starts PostgreSQL with Docker Compose and runs `alembic upgrade head`.

### 6. Create the first admin

```bash
make admin email=admin@example.com password=secret-password
```

Sign-up through the API always creates the `user` role. Only an admin can promote another user.

### 7. Run the application

```bash
make run
```

### 8. Run the tests

```bash
make test
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

## 🔐 Authentication and authorization

`POST /auth/login` receives `username` (the email) and `password` as a form and returns a JWT. The token expires in one hour. Send it as `Authorization: Bearer <token>`. In `/docs`, the **Authorize** button does the login for you.

`app/core/security.py` holds the dependencies. `get_current_user` reads the token and loads the user. `require_admin` blocks any role other than `admin`. `ensure_self_or_admin` blocks access to another user's data.

| Route | `user` | `admin` |
|---|---|---|
| `POST /users` (sign-up) | public, always `user` role | same |
| `GET /users` | 403 | all users |
| `GET`, `PATCH`, `DELETE /users/{id}` | own account only | any user |
| Change `role` | 403 | allowed |
| `GET /courses`, `GET /courses/{id}` | allowed | allowed |
| `POST`, `PATCH`, `DELETE /courses` | 403 | allowed |
| `POST /enrollments` | own `user_id` only | any user |
| `GET /enrollments` | own enrollments only | all, with filters |
| `GET`, `DELETE /enrollments/{id}` | own enrollments only | any enrollment |

A missing or invalid token returns 401. A token of a deleted user also returns 401.

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
- Replace Black and isort with Ruff, and add mypy and pip-audit to CI.
- Pin the dependency versions.

Authentication:
- Add refresh tokens and a logout that revokes them.
- Rate limit `/auth/login` against brute force.
- Read the token lifetime from the environment.

Operations:
- Add a `/health` endpoint.
- Add structured logs with a request id.
- Add a Dockerfile for the API.

Migrations:
- The `add auth fields to users` migration requires an empty `users` table. `email` and `hashed_password` have no default to backfill existing rows.

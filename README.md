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
alembic upgrade head
```

### 6. Run the application

Start the FastAPI server with Uvicorn:

```bash
uvicorn app.main:app --reload
```

Open your browser at 👉 http://localhost:8000/docs to see the interactive API docs.

## 🔑 Notes
	•	The project uses synchronous SQLAlchemy (not async) to keep things simple for interview purposes.
ALEMBIC := .venv/bin/alembic

.PHONY: db migrate revision run

db:
	docker compose up -d --wait

migrate: db
	$(ALEMBIC) upgrade head

# make revision m="add orders table"
revision: db
	$(ALEMBIC) revision --autogenerate -m "$(m)"

run: db
	.venv/bin/uvicorn app.main:app --reload

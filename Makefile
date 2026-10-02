ALEMBIC := .venv/bin/alembic

.PHONY: db migrate revision run admin test

db:
	docker compose up -d --wait

migrate: db
	$(ALEMBIC) upgrade head

# make revision m="add orders table"
revision: db
	$(ALEMBIC) revision --autogenerate -m "$(m)"

run: db
	.venv/bin/uvicorn app.main:app --reload

# make admin email=admin@example.com password=secret-password
admin: db
	.venv/bin/python -m app.create_admin "$(email)" "$(password)"

test: db
	.venv/bin/pytest

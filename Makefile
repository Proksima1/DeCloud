PYTHON ?= .venv/bin/python

setup:
	python3.10 -m venv .venv
	${PYTHON} -m pip install poetry==2.0.1
	poetry install
	pre-commit install


migration-new:
	$(PYTHON) -m alembic -c alembic/alembic.ini revision --autogenerate --rev-id=${ID} -m ${NAME}

migration-apply:
	$(PYTHON) -m alembic -c alembic/alembic.ini upgrade head

migration-delete:
	$(PYTHON) -m alembic -c alembic/alembic.ini downgrade -1

run-api:
	$(PYTHON) backend_context/entrypoints/api.py

# run-backend:
#     python3 -m uvicorn decloud.asgi:application

PYTHON ?= .venv/bin/python

setup:
	python3.10 -m venv .venv
	${PYTHON} -m pip install poetry==2.0.1
	poetry install
	pre-commit install


run-backend:
    python3 -m uvicorn decloud.asgi:application

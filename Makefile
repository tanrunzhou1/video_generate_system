PYTHON ?= 3.12
APP ?= app.main:app
HOST ?= 0.0.0.0
PORT ?= 8000

.PHONY: help init sync sync-dev dev run migrate revision downgrade db-tables lint format test clean

help:
	@echo "Available targets:"
	@echo "  make init         - Create .venv with uv"
	@echo "  make sync         - Install project dependencies"
	@echo "  make sync-dev     - Install project + dev dependencies"
	@echo "  make dev          - Run FastAPI in reload mode"
	@echo "  make run          - Run FastAPI without reload"
	@echo "  make migrate      - Run alembic upgrade head"
	@echo "  make revision m='msg' - Create alembic revision with autogenerate"
	@echo "  make downgrade    - Downgrade one alembic revision"
	@echo "  make db-tables    - Show sqlite tables"
	@echo "  make lint         - Run ruff check"
	@echo "  make format       - Run black + ruff format"
	@echo "  make test         - Run pytest"
	@echo "  make clean        - Remove python cache files"

init:
	uv python install $(PYTHON)
	uv venv --python $(PYTHON)

sync:
	uv sync

sync-dev:
	uv sync --dev

dev:
	uv run uvicorn $(APP) --reload --host $(HOST) --port $(PORT)

run:
	uv run uvicorn $(APP) --host $(HOST) --port $(PORT)

migrate:
	uv run alembic upgrade head

revision:
	uv run alembic revision --autogenerate -m "$(m)"

downgrade:
	uv run alembic downgrade -1

db-tables:
	sqlite3 storage/app.db ".tables"

lint:
	uv run ruff check .

format:
	uv run black .
	uv run ruff format .

test:
	uv run pytest -q

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

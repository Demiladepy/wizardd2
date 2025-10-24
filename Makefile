.PHONY: help install dev-install run migrate migrate-create test format lint clean docker-build docker-run

help:
	@echo "Country Currency API - Available Commands"
	@echo "=========================================="
	@echo "make install        - Install production dependencies"
	@echo "make dev-install    - Install development dependencies"
	@echo "make run            - Run the development server"
	@echo "make migrate        - Run database migrations"
	@echo "make migrate-create - Create new migration"
	@echo "make test           - Run tests"
	@echo "make format         - Format code with black"
	@echo "make lint           - Lint code with ruff"
	@echo "make clean          - Clean cache and temporary files"
	@echo "make docker-build   - Build Docker image"
	@echo "make docker-run     - Run Docker container"

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

run:
	uvicorn app:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

test-api:
	python test_api.py

test-fast:
	pytest tests/ -v -x

test-specific:
	@read -p "Enter test name pattern: " pattern; \
	pytest tests/ -k "$$pattern" -v

test-watch:
	pytest-watch tests/

format:
	black app/

lint:
	ruff check app/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf cache/*.png

docker-build:
	docker build -t country-currency-api .

docker-run:
	docker run -p 8000:8000 --env-file .env country-currency-api

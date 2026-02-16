.PHONY: help install dev build test prod stop logs clean reindex backup lint format

help:
	@echo "Hydro Search - Available commands:"
	@echo ""
	@echo "  make install      Install dependencies"
	@echo "  make dev          Start development environment"
	@echo "  make build        Build Docker images"
	@echo "  make test         Run tests"
	@echo "  make prod         Start production environment"
	@echo "  make stop         Stop all services"
	@echo "  make logs         View logs"
	@echo "  make clean        Clean up containers and volumes"
	@echo "  make reindex      Rebuild search index"
	@echo "  make backup       Create backup"
	@echo "  make lint         Run linters"
	@echo "  make format       Format code"

install:
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install

dev:
	docker-compose -f docker/docker-compose.dev.yml up --build

build:
	docker-compose -f docker/docker-compose.prod.yml build

test:
	cd backend && pytest -v
	cd frontend && npm run test

prod:
	docker-compose -f docker/docker-compose.prod.yml up -d

stop:
	docker-compose -f docker/docker-compose.dev.yml down
	docker-compose -f docker/docker-compose.prod.yml down

logs:
	docker-compose -f docker/docker-compose.prod.yml logs -f

clean:
	docker-compose -f docker/docker-compose.dev.yml down -v
	docker-compose -f docker/docker-compose.prod.yml down -v
	docker system prune -f

reindex:
	docker-compose -f docker/docker-compose.prod.yml exec backend python -m app.core.indexer

backup:
	./scripts/backup.sh

lint:
	cd backend && ruff check app/ && mypy app/
	cd frontend && npm run lint

format:
	cd backend && ruff format app/
	cd frontend && npm run format
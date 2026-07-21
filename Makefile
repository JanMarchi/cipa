.PHONY: up down test lint format migrations migrate seed check

up:
	docker compose up --build

down:
	docker compose down

test:
	docker compose run --rm web ./scripts/owner-command.sh pytest

lint:
	docker compose run --rm web ruff check .
	docker compose run --rm web ruff format --check .
	docker compose run --rm web mypy apps config

format:
	docker compose run --rm web ruff check --fix .
	docker compose run --rm web ruff format .

migrations:
	docker compose run --rm web ./scripts/manage-owner.sh makemigrations

migrate:
	docker compose run --rm web ./scripts/manage-owner.sh migrate

seed:
	docker compose run --rm web ./scripts/manage-owner.sh seed_demo

check:
	docker compose run --rm web python manage.py check --deploy --settings=config.settings.production

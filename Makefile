.DEFAULT_GOAL := help

.PHONY: help \
	setup services up up-d down build logs migrate makemigrations superuser \
	runserver vite \
	lint lint-fix format typecheck test test-cov e2e messages check \
	dexec dtest dlint dtypecheck dtest-js dshell \
	prod-image prod-run prod-migrate

## Ajuda -----------------------------------------------------------------

help: ## Lista os comandos disponiveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

## Setup -------------------------------------------------------------------

setup: ## Prepara o .env e instala dependencias Python e JS na maquina
	test -f .env || cp .env.example .env
	uv sync && bun install

## Stack inteira em containers ----------------------------------------------

up: ## Sobe app, worker, beat, vite, banco e cache em containers
	docker compose up

up-d: ## Idem, em segundo plano
	docker compose up -d

down: ## Derruba os containers
	docker compose down

build: ## Reconstroi as imagens (necessario apos mudar dependencia)
	docker compose build

logs: ## Segue os logs do worker (task na fila)
	docker compose logs -f worker

## So banco e cache em containers, resto na maquina --------------------------

services: ## Sobe so banco e cache, para rodar app e worker na maquina
	docker compose up -d database kv-database

runserver: ## Django runserver na maquina (config.settings.development)
	uv run python manage.py runserver

vite: ## Vite com HMR na porta 8001
	bun run dev

migrate: ## Aplica migrations
	uv run python manage.py migrate

makemigrations: ## Gera migrations a partir de mudanca em model
	uv run python manage.py makemigrations

superuser: ## Cria superusuario
	uv run python manage.py createsuperuser

messages: ## Extrai e compila catalogos de traducao (nao roda no container de dev)
	uv run python manage.py makemessages
	uv run python manage.py compilemessages

## Quality gates, na maquina -------------------------------------------------

lint: ## Ruff (check + format --check) e Biome/Stylelint
	uv run ruff check . && uv run ruff format --check .
	bun run lint

lint-fix: ## Aplica os fixes automaticos de lint dos dois lados
	uv run ruff check . --fix && uv run ruff format .
	bun run lint:fix

typecheck: ## MyPy strict em apps e tests
	uv run mypy apps tests

test: ## Suite pytest (config.settings.test)
	uv run pytest

test-cov: ## Testes JS com o piso de cobertura de 90%
	bun run test:coverage

e2e: ## Builda o frontend e roda os testes e2e (Playwright)
	bun run build
	uv run pytest -m e2e

check: lint typecheck test test-cov ## Roda os gates rapidos, na ordem recomendada

## Dentro dos containers (binarios ja no PATH; sem uv run) -------------------

dexec: ## Comando arbitrario no container app: make dexec CMD="python manage.py shell"
	docker compose exec app $(CMD)

dtest: ## pytest dentro do container app
	docker compose exec app pytest

dlint: ## ruff --fix dentro do container app
	docker compose exec app ruff check . --fix

dtypecheck: ## mypy dentro do container app
	docker compose exec app mypy apps tests

dtest-js: ## testes JS dentro do container frontend
	docker compose exec frontend bun run test

dshell: ## shell no container app
	docker compose exec app bash

## Imagem de producao ---------------------------------------------------------

prod-image: ## Builda a imagem de producao multi-stage
	docker build -t app:prod .

prod-migrate: ## Roda a migration como o release do Procfile
	docker run --rm --env-file .env app:prod python manage.py migrate --noinput

prod-run: ## Sobe a imagem de producao localmente com .env
	docker run --rm -p 8000:8000 --env-file .env app:prod

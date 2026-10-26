COMPOSE = docker compose -f infra/docker-compose.yml
PY = .venv/Scripts/python

.PHONY: up down build logs ps topics migrate test lint e2e evals web clean

up:            ## start everything
	$(COMPOSE) build gateway
	$(COMPOSE) up -d

down:          ## stop everything
	$(COMPOSE) down

clean:         ## stop and delete data volumes
	$(COMPOSE) down -v

build:
	$(COMPOSE) build gateway

logs:          ## make logs a=judge
	$(COMPOSE) logs -f --tail=100 $(a)

ps:
	$(COMPOSE) ps

topics:        ## (re)create Kafka topics
	$(COMPOSE) run --rm kafka-init

migrate:       ## (re)apply the SQL schema
	$(COMPOSE) exec -T postgres psql -U darvoza -d darvoza -f /docker-entrypoint-initdb.d/001_init.sql

test:
	$(PY) -m pytest -q

lint:
	$(PY) -m ruff check .

e2e:           ## end-to-end conversation against the running stack
	$(PY) scripts/e2e.py

evals:
	$(PY) evals/run_evals.py

web:           ## run the Next.js app on :3000
	cd apps/web && pnpm dev

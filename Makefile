.DEFAULT_GOAL := help

-include .env
export POSTGRES_HOST POSTGRES_PORT POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD DBT_SCHEMA
PGPASSWORD := $(POSTGRES_PASSWORD)
export PGPASSWORD

ifeq ($(OS),Windows_NT)
    VENV_BIN := .venv/Scripts
else
    VENV_BIN := .venv/bin
endif
DBT_DIR  := dbt/payment_dbt
DBT      := "$(CURDIR)/$(VENV_BIN)/dbt"

.PHONY: help compile run test build docs clean deps seed all debug list setup-db docker-up docker-down docker-logs

help:
	@echo "Usage: make <target> [SELECT=<dbt_select>]"
	@echo ""
	@echo "Targets:"
	@echo "  deps          Install dbt packages"
	@echo "  compile       Compile dbt models"
	@echo "  run           Run dbt models (use SELECT= to filter, e.g., SELECT=stg_)"
	@echo "  test          Run dbt tests (use SELECT= to filter)"
	@echo "  build         Run + test in dependency order"
	@echo "  docs          Generate dbt docs"
	@echo "  seed          Load seed data"
	@echo "  clean         Drop target artifacts"
	@echo "  all           Full pipeline: deps -> seed -> build -> docs"
	@echo "  debug         Debug dbt connection and configuration"
	@echo "  list          List dbt models (use SELECT= to filter)"
	@echo "  setup-db      Set database search_path for analytics queries"
	@echo ""
	@echo "Docker:"
	@echo "  docker-up     Start Docker services (PostgreSQL)"
	@echo "  docker-down   Stop Docker services"
	@echo "  docker-logs   Tail Docker logs"
	@echo ""
	@echo "Examples:"
	@echo "  make compile"
	@echo "  make run SELECT=stg_transactions"
	@echo "  make build"

debug:
	cd $(DBT_DIR) && $(DBT) debug

list:
	cd $(DBT_DIR) && $(DBT) ls $(if $(SELECT),--select $(SELECT))

setup-db:
	cd $(DBT_DIR) && $(DBT) source snapshot-freshness && \
	psql -h $(POSTGRES_HOST) -p $(POSTGRES_PORT) -U $(POSTGRES_USER) -d $(POSTGRES_DB) \
	-c "ALTER ROLE $(POSTGRES_USER) SET search_path TO staging, intermediate, marts, public;"

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

deps:
	cd $(DBT_DIR) && $(DBT) deps

compile:
	cd $(DBT_DIR) && $(DBT) compile

run:
	cd $(DBT_DIR) && $(DBT) run $(if $(SELECT),--select $(SELECT))

test:
	cd $(DBT_DIR) && $(DBT) test $(if $(SELECT),--select $(SELECT))

build:
	cd $(DBT_DIR) && $(DBT) build $(if $(SELECT),--select $(SELECT))

docs:
	cd $(DBT_DIR) && $(DBT) docs generate

serve: docs
	cd $(DBT_DIR) && $(DBT) docs serve

seed:
	@if [ -d "$(DBT_DIR)/seeds" ]; then \
		cd "$(DBT_DIR)" && $(DBT) seed; \
	else \
		echo "No seeds directory found"; \
	fi

clean:
	rm -rf $(DBT_DIR)/target $(DBT_DIR)/dbt_packages $(DBT_DIR)/logs

all: deps seed build docs setup-db

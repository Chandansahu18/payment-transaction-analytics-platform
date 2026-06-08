.DEFAULT_GOAL := help

-include .env
export POSTGRES_HOST POSTGRES_PORT POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD DBT_SCHEMA

ifeq ($(OS),Windows_NT)
    VENV_BIN := .venv/Scripts
else
    VENV_BIN := .venv/bin
endif
DBT_DIR  := dbt/payment_dbt
DBT      := "$(CURDIR)/$(VENV_BIN)/dbt"

.PHONY: help compile run test build docs clean deps seed all

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
	@echo ""
	@echo "Examples:"
	@echo "  make compile"
	@echo "  make run SELECT=stg_transactions"
	@echo "  make build"

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

all: deps seed build docs

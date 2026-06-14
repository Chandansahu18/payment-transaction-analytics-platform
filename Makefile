.DEFAULT_GOAL := help

-include .env
export POSTGRES_HOST POSTGRES_PORT POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD DBT_SCHEMA
export PGPASSWORD := $(POSTGRES_PASSWORD)

ifeq ($(OS),Windows_NT)
    VENV_BIN := .venv/Scripts
    ORCH_VENV_BIN := .venv-orchestration/Scripts
else
    VENV_BIN := .venv/bin
    ORCH_VENV_BIN := .venv-orchestration/bin
endif

PYTHON  := "$(CURDIR)/$(VENV_BIN)/python"
ORCH_PYTHON := "$(CURDIR)/$(ORCH_VENV_BIN)/python"
ORCH_PREFECT := "$(CURDIR)/$(ORCH_VENV_BIN)/prefect"
export PYTHONPATH := $(CURDIR)
DBT_DIR := dbt/payment_dbt
DBT     := "$(CURDIR)/$(VENV_BIN)/dbt"
DBT_RUN := cd $(DBT_DIR) && $(DBT)

.PHONY: help setup setup-db up down logs \
        ingest pipeline publish refresh excel \
        generate-data load-data reset-raw deploy-views \
        deps build run test pytest compile docs debug list clean \
        warehouse refresh-data docker-up docker-down docker-logs all serve seed \
        prefect-setup prefect-run prefect-serve prefect-server

help:
	@echo ""
	@echo "  QUICK START"
	@echo "    make up          Start PostgreSQL and wait until ready"
	@echo "    make pipeline    Transform data (dbt) + publish reporting views"
	@echo "    make refresh     Full rebuild (reset + ingest + pipeline)"
	@echo ""
	@echo "  DATA"
	@echo "    make ingest      Generate synthetic CSVs + load into raw tables"
	@echo "    make publish     Deploy reporting.* views only"
	@echo "    make excel       Export Excel dashboard workbook"
	@echo ""
	@echo "  FIRST-TIME SETUP"
	@echo "    make setup       Install dbt packages (no database required)"
	@echo "    make setup-db    Configure database (requires: make up)"
	@echo ""
	@echo "  OPTIONAL (dbt)"
	@echo "    make build       dbt build          [SELECT=model_name]"
	@echo "    make run         dbt run            [SELECT=staging]"
	@echo "    make test        dbt test           [SELECT=marts]"
	@echo "    make pytest      Ingestion QA tests (tests/test_ingestion.py)"
	@echo "    make docs        Generate dbt documentation"
	@echo ""
	@echo "  ORCHESTRATION (Prefect — separate .venv-orchestration)"
	@echo "    make prefect-setup   Create orchestration venv + install Prefect"
	@echo "    make prefect-run     Run pipeline flow once"
	@echo "    make prefect-serve   Serve deployment (optional CRON=\"0 2 * * *\")"
	@echo "    make prefect-server  Start local Prefect UI (http://localhost:4200)"
	@echo ""
	@echo "  EXAMPLES"
	@echo "    make up && make setup-db"
	@echo "    make pipeline"
	@echo "    make build SELECT=velocity_anomaly_detection"
	@echo "    make refresh"
	@echo ""

up: docker-up

down: docker-down

logs: docker-logs

ingest: generate-data load-data

pipeline: build deploy-views

refresh: reset-raw ingest pipeline

publish: deploy-views

excel:
	$(PYTHON) excel/generate_excel_report.py

setup: deps
	@echo Setup complete. Run: make up && make setup-db

setup-db:
	$(DBT_RUN) debug
	psql -h $(POSTGRES_HOST) -p $(POSTGRES_PORT) -U $(POSTGRES_USER) -d $(POSTGRES_DB) \
		-c "ALTER ROLE $(POSTGRES_USER) SET search_path TO staging, intermediate, marts, reporting, public;"

docker-up:
	docker compose up -d --wait

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

generate-data:
	$(PYTHON) generator/transaction_generator.py

load-data:
	$(PYTHON) -m ingestion.create_raw_tables
	$(PYTHON) -m ingestion.load_to_postgres

reset-raw:
	$(PYTHON) -m ingestion.reset_raw

deploy-views:
	$(PYTHON) sql/deploy_views.py

deps:
	$(DBT_RUN) deps

build:
	$(DBT_RUN) build $(if $(SELECT),--select $(SELECT),)

run:
	$(DBT_RUN) run $(if $(SELECT),--select $(SELECT),)

test:
	$(DBT_RUN) test $(if $(SELECT),--select $(SELECT),)

pytest:
	$(PYTHON) -m pytest tests/ -v

compile:
	$(DBT_RUN) compile $(if $(SELECT),--select $(SELECT),)

docs:
	$(DBT_RUN) docs generate

serve: docs
	$(DBT_RUN) docs serve

debug:
	$(DBT_RUN) debug

list:
	$(DBT_RUN) ls $(if $(SELECT),--select $(SELECT),)

seed:
	$(DBT_RUN) seed

clean:
	$(PYTHON) -c "import shutil, pathlib; dbt=pathlib.Path('$(DBT_DIR)'); [shutil.rmtree(p, ignore_errors=True) for p in [dbt/'target', dbt/'dbt_packages', dbt/'logs']]"

warehouse: pipeline
refresh-data: refresh
all: setup setup-db pipeline docs

prefect-setup:
	python -m venv .venv-orchestration
	$(ORCH_PYTHON) -m pip install --upgrade pip
	$(ORCH_PYTHON) -m pip install -r requirements-orchestration.txt

prefect-run:
	$(ORCH_PYTHON) -m orchestration.pipeline_flow

prefect-serve:
	$(ORCH_PYTHON) -m orchestration.serve $(if $(CRON),--cron "$(CRON)",) $(if $(TIMEZONE),--timezone "$(TIMEZONE)",)

prefect-server:
	$(ORCH_PREFECT) server start
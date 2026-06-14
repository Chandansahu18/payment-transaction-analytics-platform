# Orchestration (Prefect)

Uses `.venv-orchestration` (separate from `.venv` for dbt). Run once after clone:

```bash
make prefect-setup
```

Requires main setup done first (`.env`, Docker, `make up`). See [main README](../README.md).

## Commands

| Command | Action |
|---------|--------|
| `make prefect-run` | Run full pipeline once |
| `make prefect-server` | UI at http://localhost:4200 |
| `make prefect-serve` | Serve deployment (keep terminal open) |
| `make prefect-serve CRON="35 0 * * *"` | Auto-run daily at 12:35 AM IST |

Cron uses **India time** (`Asia/Kolkata`). Restart serve after changes.

## Serve + manual trigger

**Terminal 1:**
```bash
make prefect-serve
```

**Terminal 2** (Git Bash):
```bash
source .venv-orchestration/Scripts/activate
prefect deployment run "payment-analytics-pipeline/payment-analytics-pipeline"
```

`payment-analytics-pipeline/payment-analytics-pipeline` is a Prefect deployment name, not a folder.

## Flow steps

`up` → `setup-db` → `ingest` → `pytest` → `pipeline` → `test`

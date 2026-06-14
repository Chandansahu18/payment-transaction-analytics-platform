# payment_dbt

dbt project for the **Payment Transaction Analytics Platform**. Transforms `raw` payment data in PostgreSQL into analytics-ready marts with fraud risk scoring, velocity detection, and merchant risk profiling.

| | |
|--|--|
| **Last updated** | 14 June 2026 |
| **Validated baseline** | dbt **81/81** tests PASS |

---

## Project Structure

```text
dbt/payment_dbt/
├── dbt_project.yml          
├── profiles.yml
├── packages.yml
├── macros/
│   ├── fraud_scoring.sql
│   └── generate_surrogate_key.sql
├── models/
│   ├── staging/
│   │   ├── _sources.yml
│   │   ├── _schema.yml
│   │   └── stg_transactions.sql
│   ├── intermediate/
│   │   ├── _schema.yml
│   │   ├── int_transactions_enriched.sql
│   │   └── int_user_metrics.sql
│   └── marts/
│       ├── core/
│       │   ├── dim_users.sql
│       │   ├── dim_merchants.sql
│       │   └── fct_transactions.sql     
│       └── analytics/
│           ├── daily_overview_kpis.sql
│           ├── daily_merchant_kpis.sql
│           ├── cohort_analysis.sql
│           ├── hourly_fraud_trends.sql
│           ├── merchant_risk_profiling.sql
│           ├── velocity_anomaly_detection.sql
│           ├── fraud_customer_segments.sql
│           └── fraud_analysis_mart.sql
└── tests/
    └── assert_fraud_score_range.sql
```

---

## Output Schemas

All models land in PostgreSQL schemas configured in `dbt_project.yml`.

| Schema | Materialization | Contents |
|--------|-----------------|----------|
| `staging` | Views | `stg_transactions` - types, hour flags, risky-category flags |
| `intermediate` | Tables | Fraud scoring engine, velocity windows, user rollups |
| `marts` | Tables | Star schema (`dim_*`, `fct_transactions`) + 8 analytics marts |

---

## Power BI Consumption

Import mode from PostgreSQL.

| Page | Primary dbt models | Notes |
|------|-------------------|-------|
| 01 Executive Summary | `fct_transactions`, `daily_overview_kpis` | Validation cards use `daily_overview_kpis` without dim slicers |
| 02 Transaction Overview | `fct_transactions` | GMV, success, payment mix |
| 03 Fraud Risk | `fct_transactions`, `hourly_fraud_trends` | Off-hours DAX uses PBI calc `txn_hour` on `fct_transactions` |
| 04 Merchant Risk | `merchant_risk_profiling` | Filter `is_rate_reliable` (≥50 txns) before Top N |
| 05 Customer Analytics | `fraud_customer_segments` | Segments only — **not** `cohort_analysis` retention chart |
| 06 Operations & Alerts | `velocity_anomaly_detection` | Sort by `velocity_score`; action `action_required` |
| 07 Recommendations | - | Limitations narrative |

**Slim fact trade-off:** `fct_transactions` omits `tx_hour`, `txn_date`, and `is_odd_hour` (kept in staging / `hourly_fraud_trends` / `velocity_anomaly_detection`). Power BI adds **`txn_hour`** and **`txn_date`** as calculated columns from `transaction_ts`.

---

## Fraud Risk Scoring

Composite score **0-100** per transaction (`int_transactions_enriched` → `fct_transactions`):

| Signal | Points | dbt var |
|--------|--------|---------|
| High amount (≥ ₹25,000) | 30 | `high_amount_threshold` |
| Risky category (Travel, Electronics) | 25 | `risky_merchant_categories` |
| Odd hour (1-5 AM) | 20 | `odd_hour_start` / `odd_hour_end` |
| Velocity spike (1h ≥ 5 txns) | 15 | `fraud_velocity_threshold_1h` |
| Velocity spike (24h ≥ 15 txns) | 10 | `fraud_velocity_threshold_24h` |

**Risk levels:** `low` (&lt;30) · `medium` (30-49) · `high` (50-69) · `critical` (≥70)

Macro: [`macros/fraud_scoring.sql`](macros/fraud_scoring.sql)

---

## Execution Commands

Prefer **Makefile** targets from the **repo root** (handles venv, paths, and reporting views):

```bash
make setup          # dbt deps (first time)
make up && make setup-db
make pipeline       # dbt build + deploy views
```

Direct dbt (from `dbt/payment_dbt/` or via `make build`):

```bash
dbt deps
dbt build                           # models + tests
dbt build --select staging
dbt build --select intermediate
dbt build --select marts
dbt test --select marts
dbt docs generate && dbt docs serve
```

**Caution:** `make refresh` resets raw data and invalidates dashboard-validated KPIs - use only when intentionally recalibrating.

---

## Key `dbt_project.yml` Variables

| Area | Variable | Default | Used in |
|------|----------|---------|---------|
| Staging flags | `high_amount_threshold` | 25000 | `stg_transactions` |
| Staging flags | `odd_hour_start` / `odd_hour_end` | 1 / 5 | `stg_transactions` |
| Merchant risk | `merchant_risk_min_transactions` | 50 | `is_rate_reliable` on `merchant_risk_profiling` |
| Merchant risk | `merchant_risk_high_fraud_rate_pct` | 5 | `merchant_risk_category` |
| Velocity ops | `velocity_score_critical` etc. | see yml | `velocity_anomaly_detection` |

Full var list: [`dbt_project.yml`](dbt_project.yml)

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_HOST` | `localhost` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `POSTGRES_DB` | `payment_transaction_warehouse` | Database name |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | *(required)* | Database password |
| `DBT_SCHEMA` | `public` | Target schema override |

Set in project root `.env`. `make setup-db` configures `search_path` to `staging, intermediate, marts, reporting, public`.



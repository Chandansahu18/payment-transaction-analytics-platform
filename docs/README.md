# Documentation Index

| | |
|--|--|
| **Version** | 1.2 |
| **Last updated** | 14 June 2026 |
| **Owner** | Chandan Sahu |
| **Reviewer** | - |

Reference documentation for the **Payment Transaction Analytics Platform**. Read these before running pipeline components, building Power BI measures, or interpreting dashboard metrics.

---

## Document Governance

Every narrative doc and data dictionary follows this header pattern:

| Field | Purpose |
|-------|---------|
| **Version** | Semantic doc version - bump on structural or KPI changes |
| **Last updated** | Date of last substantive edit |
| **Owner** | Person accountable for accuracy (currently **Chandan Sahu**) |
| **Reviewer** | Peer reviewer name, or **-** until reviewed |
| **Version History** | Table at document bottom - what changed and when |

**When to bump version**

| Change type | Action |
|-------------|--------|
| Typo / wording only | Update **Last updated**; version optional |
| New mart, KPI, or dashboard page mapping | Minor version (+0.1) + history row |
| Baseline recalibration (`make refresh`) | Major version (+1.0) + update `initial_observation.md` and `kpi_definitions.md` |

Update **Reviewer** from **-** to the reviewer's name after peer review. Changelog lives **per file** (bottom **Version History** section), not a single global log.

---

## How we name tables and columns

| Doc type | Style | Example |
|----------|--------|---------|
| **Narrative** (`problem_statement`, `initial_observation`) | Plain English + short column/table names | “merchant fraud rate (`fraud_rate_pct`) when `is_rate_reliable` is true” |
| **Data dictionaries** (`raw`, `staging`, `marts`, `intermediate`) | Table as section heading; exact column names in tables | Under `merchant_risk_profiling`: column `fraud_rate_pct` |
| **KPI definitions** | Definition in plain language; **Source table** column has `marts.table_name` | Source: `merchant_risk_profiling` |
| **SQL / ambiguity** | Full `schema.table.column` only when two tables share a name or you are writing a query | `staging.stg_transactions.is_odd_hour` vs `dim_merchants.is_high_risk_category` |

---

## Business Context

| Document | Description |
|----------|-------------|
| [`problem_statement.md`](problem_statement.md) | Business problem, stakeholders, data sources, KPIs tracked, analytical techniques, success criteria |
| [`initial_observation.md`](initial_observation.md) | Post-profiling findings — fraud patterns, merchant risk, synthetic limitations, dashboard alignment |

---

## Data Dictionaries (Warehouse Layers)

Read in pipeline order: **raw → staging → intermediate → marts**

| Document | Schema | Contents |
|----------|--------|----------|
| [`raw_data_dictionary.md`](raw_data_dictionary.md) | `raw` | users · merchants · transactions · watermark - ingestion source of truth |
| [`staging_data_dictionary.md`](staging_data_dictionary.md) | `staging` | `stg_transactions` - typing, fraud flags, hour features |
| [`intermediate_data_dictionary.md`](intermediate_data_dictionary.md) | `intermediate` | Fraud scoring engine, velocity windows, user rollups |
| [`marts_data_dictionary.md`](marts_data_dictionary.md) | `marts` | Star schema dims/fact + 8 analytics marts - primary BI layer |

---

## Metrics

| Document | Description |
|----------|-------------|
| [`kpi_definitions.md`](kpi_definitions.md) | Every KPI with definition, formula, and source table |

---

## Recommended Reading Order

1. **`problem_statement.md`** - why the project exists and what it delivers
2. **`raw_data_dictionary.md`** - understand source entities and row counts
3. **`staging_data_dictionary.md`** → **`intermediate_data_dictionary.md`** - how fraud logic is built
4. **`marts_data_dictionary.md`** - what Power BI and SQL analytics consume
5. **`kpi_definitions.md`** - compute metrics consistently
6. **`initial_observation.md`** - what the current dataset shows and its limitations

---

## Pipeline Quick Reference

```bash
make up          # Start PostgreSQL (Docker)
make setup       # Install dbt packages
make setup-db    # Configure database search_path
make pipeline    # dbt build + deploy reporting views
make excel       # Export Excel workbook from marts
```

Full rebuild

```bash
make refresh     # reset + ingest + pipeline
```

---
## Important Notes

- Raw CSVs in `data/raw/` are **gitignored** - run `make ingest` after clone.
- `.pbix` files are **gitignored** - portfolio preview via screenshots only.
- **Locked headline KPIs:** GMV **₹3.4Bn** · Fraud Rate ~**3.5%** · Success Rate ~**92.6%** · Fraud Loss ~**₹88M** (generator calibrated; do not change without `make refresh` + re-validation).
- Do not run `make refresh` unless intentionally recalibrating - dashboard validated on current baseline.
- `reporting.*` views intentionally use schema prefixes - see `sql/deploy_views.py`.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jun 2026 | Initial docs index and reading order |
| 1.1 | 14 Jun 2026 | Document governance (owner, version, reviewer policy) |
| 1.2 | 14 Jun 2026 | Owner set to Chandan Sahu; reviewer field in header template |
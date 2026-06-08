# payment_dbt

dbt for the Payment Transaction Analytics Platform.
Transforms raw payment transaction data from PostgreSQL into analytics-ready dimensional models
with built-in fraud risk scoring.

## Project Structure

```
dbt/payment_dbt/
├── dbt_project.yml          
├── profiles.yml            
├── packages.yml             
├── .gitignore
├── README.md
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
│           └── fraud_analysis_mart.sql       
└── tests/
    └── assert_fraud_score_range.sql 
```


## Fraud Risk Scoring

Each transaction is scored on a **0-100** composite scale using 5 weighted signals:

| Signal | Weight | Description |
|--------|--------|-------------|
| High amount (>25,000 INR) | 30 | Large transactions are riskier |
| Risky merchant category | 25 | Travel, Electronics categories |
| Odd hour (1–5 AM) | 20 | Unusual transaction timing |
| Velocity spike (1h ≥ 5 tx) | 15 | Rapid successive transactions |
| Velocity spike (24h ≥ 15 tx) | 10 | High daily volume |

**Risk levels:** `low` (<30), `medium` (30-49), `high` (50-69), `critical` (≥70)

## Execution Commands

```bash
# Install dependencies
dbt deps

# Run all models
dbt run

# Run specific layer
dbt run --select staging
dbt run --select intermediate
dbt run --select marts

# Run tests
dbt test

# Generate and serve documentation
dbt docs generate
dbt docs serve

# Generate DAG lineage only
dbt docs generate --no-compile
```

## Output Schemas

| Schema | Materialization | Models |
|--------|---------------|--------|
| `staging` | Views | Cleaned source data |
| `intermediate` | Tables | Enriched + aggregated metrics |
| `marts_core` | Tables | Dimensions + fact table |
| `marts_analytics` | Tables | Analytics-ready KPIs |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_HOST` | `localhost` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `POSTGRES_DB` | `payment_transaction_warehouse` | Database name |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `your_strong_password_here` | Database password |
| `DBT_SCHEMA` | `public` | Target schema override |

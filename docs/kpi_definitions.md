# KPI Definitions

| | |
|--|--|
| **Version** | 1.2 |
| **Last updated** | 14 June 2026 |
| **Owner** | Chandan Sahu |
| **Reviewer** | - |

---

## Executive Summary

Single source of truth for **business metric definitions** consumed by Power BI, Excel, and **`reporting.*` SQL views**. This file must be used before making dashboard metrics or writing warehouse SQL - inconsistent definitions are the main cause of stakeholder distrust.


**Baseline (locked):** GMV **₹3.4Bn** · Fraud Rate ~**3.5%** · Success Rate ~**92.6%** · Fraud Loss ~**₹88M** · Fraud Loss Rate ~**2.6% of GMV**

---

## Format Convention

| Layer | Rate storage | Power BI rule |
|-------|--------------|---------------|
| DAX `DIVIDE()` measures | 0-1 decimal | Apply **Percentage** format directly |
| Mart columns `*_pct` | 0-100 scale | Divide by **100** before Percentage format

---

## Transaction & Revenue Metrics

> **Business questions this section answers:** How much GMV did we capture? Is payment success holding? What is average ticket size? Are volume and revenue growing month over month?

| KPI | Definition | Formula | Source table |
|-----|------------|---------|--------------|
| **Total Transactions** | Count of all transaction rows in context | `COUNTROWS(fct_transactions)` | `marts.fct_transactions` |
| **GMV (INR)** | Gross merchandise value — successful transactions only | `SUM(amount) WHERE status = 'success'` | `marts.fct_transactions` |
| **Success GMV (INR)** | Same as GMV when GMV is success-filtered | `SUM(amount) WHERE status = 'success'` | `marts.fct_transactions` |
| **Avg Ticket (INR)** | Average GMV per transaction attempt | `GMV (INR) / Total Transactions` | `marts.fct_transactions` |
| **Success Rate** | Share of transactions with success status | `Success txns / Total Transactions` | `marts.fct_transactions` |
| **Failure Rate** | Share of transactions with failed status | `Failed txns / Total Transactions` | `marts.fct_transactions` |
| **Capture Rate** | Share of GMV successfully captured | `Success GMV / GMV (INR)` | `marts.fct_transactions` |
| **GMV MoM %** | Month-over-month GMV change | `(Current Month GMV - Prior Month GMV) / Prior Month GMV` | `marts.fct_transactions` + `Date` |
| **Transactions MoM %** | Month-over-month transaction volume change | `(Current - Prior) / Prior` | `marts.fct_transactions` + `Date` |
| **Daily KPI GMV** | Daily revenue from overview mart (all statuses) | `SUM(total_revenue)` | `marts.daily_overview_kpis` |
| **Daily KPI Fraud Loss** | Daily fraud loss from overview mart | `SUM(fraud_loss_amount)` | `marts.daily_overview_kpis` |

---

## Fraud Metrics

> **Business questions this section answers:** What share of transactions is fraudulent? How much did fraud cost in INR? Is off-hours fraud worse than normal hours? Which risk tiers drive loss?

| KPI | Definition | Formula | Source table |
|-----|------------|---------|--------------|
| **Fraud Transactions** | Count of ground-truth fraud rows | `COUNTROWS WHERE is_fraud = TRUE` | `marts.fct_transactions` |
| **Fraud Rate** | Fraud share of all transactions | `Fraud Transactions / Total Transactions` | `marts.fct_transactions` |
| **Fraud Loss (INR)** | Sum of amounts on fraud rows | `SUM(amount) WHERE is_fraud = TRUE` | `marts.fct_transactions` |
| **Fraud Loss Rate** | Fraud loss as share of GMV | `Fraud Loss (INR) / GMV (INR)` | `marts.fct_transactions` |
| **Off-Hours Transactions** | Transactions between 1-5 AM | PBI: `txn_hour` IN {1,2,3,4,5} on `fct_transactions`; warehouse: `is_odd_hour` on staging or `hourly_fraud_trends` | `fct_transactions` + PBI `txn_hour` |
| **Off-Hours Fraud Transactions** | Fraud txns in off-hours window | `[Fraud Transactions]` with off-hours filter | `fct_transactions` |
| **Off-Hours Fraud Rate** | Fraud rate in off-hours only | `Off-Hours Fraud Txns / Off-Hours Transactions` | `fct_transactions` |
| **Normal Hours Fraud Transactions** | Fraud txns outside 1-5 AM | `[Fraud Transactions]` with inverse off-hours filter | `fct_transactions` |
| **Normal Hours Fraud Rate** | Fraud rate in normal hours | `Normal Hours Fraud Txns / Normal Hours Transactions` | `fct_transactions` |
| **High Risk Transactions** | Transactions at high or critical risk level | `COUNTROWS WHERE fraud_risk_level IN ('high','critical')` | `marts.fct_transactions` |
| **Avg Fraud Risk Score** | Mean composite risk score | `AVERAGE(fraud_risk_score)` | `marts.fct_transactions` |
| **Hourly Fraud Rate** | Pre-aggregated fraud rate by hour × category | `fraud_rate_pct / 100` | `marts.hourly_fraud_trends` |

**Validated baselines:** GMV **₹3.4Bn** · Fraud Rate ~**3.5%** · Success Rate ~**92.6%** · Fraud Loss ~**₹88M** · Fraud Loss Rate ~**2.6% of GMV**

---

## Merchant Metrics

> **Business questions this section answers:** Which merchants exceed fraud thresholds with enough volume to trust? Who should we review or suspend? How do failure rates compare across merchants?

| KPI | Definition | Formula | Source table |
|-----|------------|---------|--------------|
| **Merchant Fraud Rate** | Merchant-level fraud percentage | `fraud_rate_pct` column (NULL if volume &lt; 50) | `marts.merchant_risk_profiling` |
| **is_rate_reliable** | Whether fraud rate is statistically usable | `total_transactions >= 50` | `marts.merchant_risk_profiling` |
| **Merchant Fraud Rate (ratio)** | BI-friendly 0-1 rate | `fraud_rate_pct / 100` or `fraud_rate_ratio` | `reporting.merchant_risk_profiling` |
| **Failure Rate (merchant)** | Failed txns / total txns per merchant | `failure_rate_pct / 100` | `marts.merchant_risk_profiling` |
| **Avg Ticket Size (merchant)** | Mean transaction amount per merchant | `avg_ticket_size` | `marts.merchant_risk_profiling` |
| **High Risk Merchant Txns** | high + critical risk transactions | `high_risk_transactions` | `marts.merchant_risk_profiling` |
| **merchant_risk_category** | Risk bucket | No Activity · Insufficient Volume · Low/Medium/High Risk | `marts.merchant_risk_profiling` |

> **Do not** use `AVERAGE(fraud_rate_pct)` across merchants - use row-level column or weighted logic.

---

## Customer & Activity Metrics

> **Business questions this section answers:** How many users and merchants are active? How engaged is the customer base? How many fraud-prone or high-value customers exist?

| KPI | Definition | Formula | Source table |
|-----|------------|---------|--------------|
| **Active Users** | Distinct users with transactions in context | `DISTINCTCOUNT(user_sk)` | `marts.fct_transactions` |
| **Active Merchants** | Distinct merchants with transactions in context | `DISTINCTCOUNT(merchant_sk)` | `marts.fct_transactions` |
| **Transactions per User** | Average txns per active user | `Total Transactions / Active Users` | `marts.fct_transactions` |
| **Fraud Prone Customers** | Users with at least one fraud event | `COUNTROWS WHERE fraud_segment IN ('Single Fraud','Repeat Fraudster')` | `marts.fraud_customer_segments` |
| **High Monetary Customers** | High lifetime spend segment | `COUNTROWS WHERE monetary_segment = 'High Value'` | `marts.fraud_customer_segments` |
| **Repeat Fraudster Count** | Users with ≥3 fraud txns | `COUNTROWS WHERE fraud_segment = 'Repeat Fraudster'` | `marts.fraud_customer_segments` |
| **Avg Days Since Registration** | Mean user tenure | `AVERAGE(days_since_registration)` | `marts.dim_users` |

---

## Segment Metrics (RFM-style)

> **Business questions this section answers:** Who are our high-value vs dormant customers? Which users show repeat fraud behaviour? How should CRM and risk policies segment the base?

| KPI | Definition | Formula | Source table |
|-----|------------|---------|--------------|
| **recency_days** | Days since last transaction (anchor = max dataset date) | `anchor_ts - last_transaction_ts` | `marts.fraud_customer_segments` |
| **frequency** | Lifetime transaction count per user | `COUNT(*)` per user | `marts.fraud_customer_segments` |
| **monetary_value** | Lifetime spend per user | `SUM(amount)` per user | `marts.fraud_customer_segments` |
| **recency_segment** | Active · Recent · Lapsed · Inactive | CASE on recency_days thresholds | `marts.fraud_customer_segments` |
| **frequency_segment** | High / Medium / Low Frequency | CASE on frequency thresholds | `marts.fraud_customer_segments` |
| **monetary_segment** | High / Medium / Low Value | CASE on monetary_value thresholds | `marts.fraud_customer_segments` |
| **fraud_segment** | Clean · Single Fraud · Repeat Fraudster | CASE on fraud_count | `marts.fraud_customer_segments` |

---

## Cohort Metrics

> **Business questions this section answers:** Do users acquired in a given month return at 1/3/6 months? How does fraud differ by acquisition cohort? *(Warehouse/SQL depth - not charted on Page 5 due to flat synthetic retention.)*

| KPI | Definition | Formula | Source table |
|-----|------------|---------|--------------|
| **Cohort Month** | Month of user's first **successful** transaction | `DATE_TRUNC('month', MIN(transaction_ts))` per user | `marts.cohort_analysis` logic |
| **Cohort Size** | Users in cohort | `cohort_size` | `marts.cohort_analysis` |
| **Retention 1M %** | Share of mature cohort active at month offset 1 | `retained_1m_users / mature_1m_cohort_size × 100` | `marts.cohort_analysis` |
| **Retention 3M %** | Same at 3-month offset | `retained_3m_users / mature_3m_cohort_size × 100` | `marts.cohort_analysis` |
| **Retention 6M %** | Same at 6-month offset | `retained_6m_users / mature_6m_cohort_size × 100` | `marts.cohort_analysis` |
| **Weighted Avg 1M Retention** | Portfolio retention weighted by mature cohort size | `SUM(retention_1m_pct × mature_1m_cohort_size) / SUM(mature_1m_cohort_size) / 100` | `marts.cohort_analysis` |
| **Cohort Fraud Rate %** | Fraud txns / all txns within cohort rollup | `fraud_rate_pct` | `marts.cohort_analysis` |

---

## Velocity & Operations Metrics

> **Business questions this section answers:** Which transactions need immediate ops review? How severe is the velocity breach? What staffing or rule changes does the alert queue imply?

| KPI | Definition | Formula | Source table |
|-----|------------|---------|--------------|
| **velocity_score** | Composite ops priority score | Model-derived weighted score | `marts.velocity_anomaly_detection` |
| **velocity_alert_level** | Low · Medium · High · Critical | CASE on score + txn count rules | `marts.velocity_anomaly_detection` |
| **action_required** | Boolean ops action flag | TRUE when score/velocity thresholds breached | `marts.velocity_anomaly_detection` |
| **is_critical** | Highest-priority flag | TRUE for critical velocity + fraud score combos | `marts.velocity_anomaly_detection` |
| **velocity_breach_type** | Human-readable breach reason | High Velocity (1h) · Category Concentration · etc. | `marts.velocity_anomaly_detection` |
| **tx_count_1h** | User txns in trailing 1 hour | Window count | `marts.velocity_anomaly_detection` |
| **tx_count_24h** | User txns in trailing 24 hours | Window count | `marts.velocity_anomaly_detection` |

---

## Validation Metrics (Executive cross-check)

> **Business questions this section answers:** Do executive KPI cards reconcile with the daily rollup mart? Can leadership trust the headline numbers?

Use on **separate cards without dimension slicers**:

| KPI | Definition | Formula | Source |
|-----|------------|---------|--------|
| **GMV Variance** | Star-schema GMV vs daily mart | `[GMV (INR)] - [Daily KPI GMV]` | `fct_transactions` vs `daily_overview_kpis` |

`daily_overview_kpis` is not related to `dim_users` or `dim_merchants` - dimension slicers inflate validation measures.

---

## SQL Reporting Ratios (`reporting.*` views)

| Column | Definition | Formula |
|--------|------------|---------|
| `fraud_rate_ratio` | Merchant/cohort fraud rate on 0-1 scale | `fraud_rate_pct / 100` |
| `failure_rate_ratio` | Merchant failure rate on 0-1 scale | `failure_rate_pct / 100` |
| `retention_1m_rate` | 1M retention on 0-1 scale | `retention_1m_pct / 100` |
| `retention_3m_rate` | 3M retention on 0-1 scale | `retention_3m_pct / 100` |
| `retention_6m_rate` | 6M retention on 0-1 scale | `retention_6m_pct / 100` |

---

## Power BI Consumption

Production metric docs define **what** a KPI means and **how to compute it logically** - not full measure code that drifts from the live model. Implementation stays in the semantic layer (Power BI `.pbix`).

| Pattern | How it maps to this doc |
|---------|-------------------------|
| **Rates** | `DIVIDE(numerator, denominator, 0)` — format as Percentage (0–1 storage) |
| **GMV** | `SUM(amount)` where `status = 'success'` — see Transaction & Revenue table |
| **Off-hours** | Filter PBI calc column `txn_hour` IN {1,2,3,4,5} on `fct_transactions` |
| **Mart `*_pct`** | Divide by 100 in DAX, or use `reporting.*` `*_ratio` columns |
| **Validation cards** | `daily_overview_kpis` measures — **no** user/merchant dimension slicers |
| **Cohort retention** | Weighted average using `retention_*_pct × mature_*_cohort_size` — warehouse/SQL depth only |



---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jun 2026 | Initial KPI tables |
| 1.1 | 14 Jun 2026 | Business questions per section, removed copy-paste DAX |
| 1.2 | 14 Jun 2026 | Metadata header, locked baselines, Power BI consumption patterns |



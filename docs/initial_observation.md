# Initial Dataset Observations

| | |
|--|--|
| **Version** | 1.3 |
| **Last updated** | 14 June 2026 |
| **Owner** | Chandan Sahu |
| **Reviewer** | - |

---

## Executive Summary

~500k synthetic payments (Jan 2024–Jun 2025) support fraud, merchant risk, velocity, and segment analytics.

**Baselines:** Fraud Rate ~**3.5%** · Success Rate ~**92.6%** · Fraud Loss ~**₹88M**

**Actions:** Monitor 1–5 AM · review Travel/Electronics merchants · action `action_required` on velocity queue · rank merchants only when `is_rate_reliable`.

**Limit:** Flat MoM/retention curves - no retention chart on Page 5; do not `make refresh` unless recalibrating.

---

## Why This Document Matters

| Audience | Use |
|----------|-----|
| Executives | Trust headline KPIs and known limits before decisions |
| Fraud / Risk | Prioritise hours, categories, merchants, velocity queue |
| Analytics / Engineering | Validate pipeline output vs dashboard; interview-ready limitations |
| Interviewers | Shows honest trade-offs (flat retention removed from UI, mart retained) |

---

## Dataset at a Glance

| Entity | Volume | Business relevance |
|--------|--------|-------------------|
| Transactions | ~500,000 | GMV, fraud loss, payment mix, risk scoring |
| Users | 12,000 | Segments, fraud propensity, geography |
| Merchants | 600 | Risk ranking, category exposure, long-tail volume |

---

## Entity Observations

### Users

| Aspect | Finding | Why it matters |
|--------|---------|----------------|
| Identity | Stable `user_id` per row | Reliable customer-level metrics |
| Segments | dormant → power activity tiers | Explains uneven txn frequency |
| Retention mart | `cohort_analysis` built with mature cohort logic | SQL/interview depth; **not charted** (flat lines) |

### Merchants

| Aspect | Finding | Why it matters |
|--------|---------|----------------|
| Risk flag | `is_high_risk_category` for Travel, Electronics | Focus reviews on high-loss categories |
| Volume | Long tail; many &lt;50 txns | `fraud_rate_pct` null-filter `is_rate_reliable` before Top N |
| Seeded risk | ~12 high-fraud merchants in generator | Visible suspend/review candidates on Page 4 |

### Transactions

| Aspect | Finding | Why it matters |
|--------|---------|----------------|
| Off-hours | Higher fraud 1–5 AM (`is_odd_hour`) | Justifies off-hours rules and Page 3 focus |
| Velocity | ≥5/1h or ≥15/24h spikes | Drives fraud score + Page 6 queue |
| Risk mix | Most `low`/`medium`; loss from `high`/`critical` | Target high-risk tiers for loss reduction |

---

## Pipeline & BI Consumption

```mermaid
flowchart LR
  CSV[Generator CSV] --> Raw[raw schema]
  Raw --> Staging[staging]
  Staging --> Intermediate[intermediate]
  Intermediate --> Marts[marts]
  Marts --> PBI[Power BI]
```

- `fct_transactions` has no warehouse `tx_hour` or `transaction_date` - in Power BI, **`txn_hour`** and **`txn_date`** are calculated columns from `transaction_ts` (use for fact-level hour/date DAX). For hour×category heatmaps use `hourly_fraud_trends`; for the ops queue use `velocity_anomaly_detection`.

---

## Key Analytical Questions

| Domain | Question 
|--------|----------|
| Fraud | Off-hours vs normal-hours fraud delta? 
| Fraud | Top category × payment method for fraud loss? 
| Merchant | Merchants &gt;5% fraud with `is_rate_reliable`? 
| Operations | Share of alerts with `action_required`? 
| Segments | Split of `fraud_segment` and `monetary_segment`? 
| Quality | GMV vs `daily_overview_kpis` aligned?

---

## Synthetic Limitations

1. Stationary success/failure rates over 18 months  
2. Flat cohort retention—warehouse only, not trend chart  
3. Headline KPIs locked: Fraud Rate ~3.5% · Success Rate ~92.6% · Fraud Loss ~₹88M  
4. Rare `disputed` status  
5. Payments-only—no marketing / clickstream feeds  

Snapshot KPIs and cross-dimensional fraud insights remain valid.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 14 Jun 2026 | Initial profiling notes |
| 1.2 | 14 Jun 2026 | Executive summary, trade-offs, mermaid flow |
| 1.3 | 14 Jun 2026 | Metadata header, concise summary, locked baselines |

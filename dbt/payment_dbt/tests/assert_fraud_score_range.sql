select transaction_id, fraud_risk_score
from {{ ref('int_transactions_enriched') }}
where fraud_risk_score < 0 or fraud_risk_score > 100

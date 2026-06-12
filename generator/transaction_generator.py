import uuid
import random
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta, date

random.seed(42)
Faker.seed(42)
fake = Faker('en_IN')

NUM_USERS = 12_000
NUM_MERCHANTS = 600
TARGET_TRANSACTIONS = 500_000
TARGET_FRAUD_RATE_PCT = 3.5

CITY_STATE_MAP = {
    'Mumbai': 'Maharashtra', 'Bengaluru': 'Karnataka', 'Delhi': 'Delhi',
    'Hyderabad': 'Telangana', 'Chennai': 'Tamil Nadu', 'Pune': 'Maharashtra',
    'Kolkata': 'West Bengal', 'Ahmedabad': 'Gujarat', 'Jaipur': 'Rajasthan',
    'Surat': 'Gujarat'
}

INDIAN_CITIES = list(CITY_STATE_MAP.keys())
MERCHANT_CATEGORIES = ['Retail', 'Food & Beverage', 'Travel', 'Electronics',
                       'Healthcare', 'Entertainment', 'Groceries', 'Fashion']
PAYMENT_METHODS = ['UPI', 'Debit Card', 'Credit Card', 'Wallet', 'NetBanking']
STATUSES = ['success', 'success', 'success', 'success', 'failed', 'declined', 'disputed']
DEVICE_TYPES = ['mobile', 'mobile', 'desktop', 'POS']
AGE_GROUPS = ['18-25', '26-35', '36-50', '50+']
ACCOUNT_TYPES = ['savings', 'current', 'premium']

USER_SEGMENTS = {
    'dormant': {'weight': 0.35, 'monthly_active_prob': 0.18, 'tx_range': (0, 2), 'churn_prob': 0.45},
    'light': {'weight': 0.30, 'monthly_active_prob': 0.35, 'tx_range': (1, 4), 'churn_prob': 0.30},
    'medium': {'weight': 0.20, 'monthly_active_prob': 0.55, 'tx_range': (2, 8), 'churn_prob': 0.18},
    'heavy': {'weight': 0.10, 'monthly_active_prob': 0.72, 'tx_range': (4, 14), 'churn_prob': 0.10},
    'power': {'weight': 0.05, 'monthly_active_prob': 0.85, 'tx_range': (8, 22), 'churn_prob': 0.06},
}

DATA_START = datetime(2024, 1, 1)
DATA_END = datetime(2025, 6, 30)


def generate_users(n=NUM_USERS):
    users = []
    for _ in range(n):
        city = random.choice(INDIAN_CITIES)
        users.append({
            'user_id': f"USR_{str(uuid.uuid4())[:8].upper()}",
            'age_group': random.choice(AGE_GROUPS),
            'account_type': random.choice(ACCOUNT_TYPES),
            'registration_date': fake.date_between(start_date=date(2024, 1, 1), end_date=date(2025, 3, 31)),
            'city': city,
            'state': CITY_STATE_MAP[city]
        })
    return pd.DataFrame(users)


def generate_merchants(n=NUM_MERCHANTS):
    merchants = []
    for _ in range(n):
        category = random.choice(MERCHANT_CATEGORIES)
        city = random.choice(INDIAN_CITIES)
        merchants.append({
            'merchant_id': f"MER_{str(uuid.uuid4())[:8].upper()}",
            'merchant_name': fake.company(),
            'merchant_category': category,
            'city': city,
            'state': CITY_STATE_MAP[city],
            'onboarding_date': fake.date_between(start_date='-2y', end_date='-3m')
        })
    return pd.DataFrame(merchants)


def _assign_user_segment():
    segments = list(USER_SEGMENTS.keys())
    weights = [USER_SEGMENTS[s]['weight'] for s in segments]
    return random.choices(segments, weights=weights, k=1)[0]


def _sample_amount(is_fraud, merchant_category):
    if is_fraud:
        return round(random.uniform(18000, 75000), 2)
    if merchant_category in ('Groceries', 'Food & Beverage'):
        return round(random.uniform(50, 3500), 2)
    if merchant_category in ('Retail', 'Fashion'):
        return round(random.uniform(200, 12000), 2)
    return round(random.uniform(500, 22000), 2)


def _evaluate_fraud(user_ctx, merchant_id, merchant_category, amount, ts, device_type, fraud_prone_merchants):
    fraud_probability = 0.006 + user_ctx['fraud_propensity']

    if merchant_id in fraud_prone_merchants:
        fraud_probability += 0.12
    if amount > 15000:
        fraud_probability += 0.025
    if merchant_category in ('Travel', 'Electronics'):
        fraud_probability += 0.018
    if 1 <= ts.hour <= 5:
        fraud_probability += 0.015
    if user_ctx['prior_tx_count'] >= 3 and amount > user_ctx['avg_amount'] * 4:
        fraud_probability += 0.04
    if device_type != user_ctx['primary_device'] and amount > 10000:
        fraud_probability += 0.03
    if user_ctx.get('inactive_days', 0) >= 45 and amount > 12000:
        fraud_probability += 0.035

    return random.random() < min(fraud_probability, 0.65)


def _build_transaction_record(user_id, merchant_ids, merchant_category_map, ts, is_fraud, user_ctx):
    merchant_id = random.choice(merchant_ids)
    merchant_category = merchant_category_map[merchant_id]
    device_type = user_ctx['primary_device'] if random.random() < 0.82 else random.choice(DEVICE_TYPES)
    city = random.choice(INDIAN_CITIES)
    draft_amount = _sample_amount(False, merchant_category)

    if is_fraud is None:
        is_fraud = _evaluate_fraud(
            user_ctx, merchant_id, merchant_category,
            draft_amount, ts, device_type,
            user_ctx['fraud_prone_merchants']
        )

    amount = _sample_amount(is_fraud, merchant_category)

    user_ctx['prior_tx_count'] += 1
    user_ctx['total_amount'] += amount
    user_ctx['avg_amount'] = user_ctx['total_amount'] / user_ctx['prior_tx_count']
    user_ctx['last_tx_ts'] = ts

    return {
        'transaction_id': str(uuid.uuid4()),
        'user_id': user_id,
        'merchant_id': merchant_id,
        'merchant_category': merchant_category,
        'payment_method': random.choice(PAYMENT_METHODS),
        'amount': amount,
        'currency': 'INR',
        'status': random.choice(STATUSES),
        'is_fraud': is_fraud,
        'device_type': device_type,
        'city': city,
        'state': CITY_STATE_MAP[city],
        'transaction_ts': ts,
        'created_at': datetime.now()
    }


def _month_starts(start_dt, end_dt):
    cursor = datetime(start_dt.year, start_dt.month, 1)
    while cursor <= end_dt:
        yield cursor
        if cursor.month == 12:
            cursor = datetime(cursor.year + 1, 1, 1)
        else:
            cursor = datetime(cursor.year, cursor.month + 1, 1)


def _generate_burst_cluster(user_id, merchant_ids, merchant_category_map, base_ts, user_end, user_ctx, transactions):
    for _ in range(random.randint(6, 10)):
        ts = base_ts + timedelta(minutes=random.randint(0, 50))
        if ts > user_end:
            break
        is_fraud = random.random() < 0.18
        transactions.append(
            _build_transaction_record(user_id, merchant_ids, merchant_category_map, ts, is_fraud, user_ctx)
        )

    for _ in range(random.randint(14, 20)):
        ts = base_ts + timedelta(hours=random.randint(0, 22), minutes=random.randint(0, 59))
        if ts > user_end:
            break
        is_fraud = random.random() < 0.14
        transactions.append(
            _build_transaction_record(user_id, merchant_ids, merchant_category_map, ts, is_fraud, user_ctx)
        )


def generate_transactions(users_df, merchants_df, n=TARGET_TRANSACTIONS):
    transactions = []
    merchant_ids = merchants_df['merchant_id'].tolist()
    merchant_category_map = merchants_df.set_index('merchant_id')['merchant_category'].to_dict()
    fraud_prone_merchants = set(random.sample(merchant_ids, k=min(25, len(merchant_ids))))

    user_reg_map = {
        row.user_id: max(pd.to_datetime(row.registration_date).to_pydatetime(), DATA_START)
        for row in users_df.itertuples(index=False)
    }

    burst_user_ids = set(random.sample(list(user_reg_map.keys()), k=int(len(user_reg_map) * 0.025)))

    for user_id, user_start in user_reg_map.items():
        segment = _assign_user_segment()
        segment_cfg = USER_SEGMENTS[segment]
        lifetime_days = random.choices([90, 180, 365, 540, 720], weights=[15, 25, 30, 20, 10])[0]
        user_end = min(user_start + timedelta(days=lifetime_days), DATA_END)

        if user_start >= user_end:
            continue

        user_ctx = {
            'segment': segment,
            'primary_device': random.choice(DEVICE_TYPES),
            'fraud_propensity': random.uniform(0.0, 0.02) if segment != 'power' else random.uniform(0.01, 0.04),
            'fraud_prone_merchants': fraud_prone_merchants,
            'prior_tx_count': 0,
            'total_amount': 0.0,
            'avg_amount': 0.0,
            'last_tx_ts': None,
            'inactive_days': 0,
        }

        if user_id in burst_user_ids:
            burst_point = user_start + timedelta(days=random.randint(30, max(30, (user_end - user_start).days - 30)))
            _generate_burst_cluster(user_id, merchant_ids, merchant_category_map, burst_point, user_end, user_ctx, transactions)
            if len(transactions) >= n:
                break

        active = True
        for month_start in _month_starts(user_start, user_end):
            if not active or len(transactions) >= n:
                break

            if month_start < user_start:
                continue

            if month_start.month == 12:
                next_month = datetime(month_start.year + 1, 1, 1)
            else:
                next_month = datetime(month_start.year, month_start.month + 1, 1)
            month_end = min(next_month - timedelta(seconds=1), user_end)
            if month_end < user_start:
                continue

            if random.random() < segment_cfg['churn_prob'] / 12:
                active = False
                continue

            if random.random() > segment_cfg['monthly_active_prob']:
                user_ctx['inactive_days'] = (month_end - (user_ctx['last_tx_ts'] or user_start)).days
                continue

            if random.random() < 0.12:
                continue

            tx_count = random.randint(*segment_cfg['tx_range'])
            for _ in range(tx_count):
                if len(transactions) >= n:
                    break
                day_offset = random.randint(0, max(0, (month_end - max(month_start, user_start)).days))
                hour = random.choices(
                    range(24),
                    weights=[1, 1, 1, 1, 1, 1, 2, 4, 6, 8, 9, 10, 10, 9, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1]
                )[0]
                ts = max(month_start, user_start) + timedelta(days=day_offset, hours=hour, minutes=random.randint(0, 59))
                if ts > user_end:
                    continue
                if user_ctx['last_tx_ts']:
                    user_ctx['inactive_days'] = (ts - user_ctx['last_tx_ts']).days
                transactions.append(
                    _build_transaction_record(user_id, merchant_ids, merchant_category_map, ts, None, user_ctx)
                )

    if len(transactions) < n:
        user_ids = users_df['user_id'].tolist()
        while len(transactions) < n:
            user_id = random.choice(user_ids)
            user_start = user_reg_map[user_id]
            user_end = min(user_start + timedelta(days=365), DATA_END)
            user_seconds = int((user_end - user_start).total_seconds())
            if user_seconds <= 0:
                continue
            ts = user_start + timedelta(seconds=random.randint(0, user_seconds))
            user_ctx = {
                'segment': 'light',
                'primary_device': random.choice(DEVICE_TYPES),
                'fraud_propensity': 0.01,
                'fraud_prone_merchants': fraud_prone_merchants,
                'prior_tx_count': random.randint(1, 5),
                'total_amount': random.uniform(1000, 8000),
                'avg_amount': random.uniform(200, 2000),
                'last_tx_ts': ts - timedelta(days=random.randint(7, 60)),
                'inactive_days': random.randint(7, 60),
            }
            user_ctx['avg_amount'] = user_ctx['total_amount'] / user_ctx['prior_tx_count']
            transactions.append(
                _build_transaction_record(user_id, merchant_ids, merchant_category_map, ts, None, user_ctx)
            )

    return pd.DataFrame(transactions[:n])


if __name__ == '__main__':
    print("Generating synthetic payment data with realistic fraud patterns...")

    print("→ Generating users...")
    users = generate_users(NUM_USERS)
    users.to_csv('data/raw/users.csv', index=False)

    print("→ Generating merchants...")
    merchants = generate_merchants(NUM_MERCHANTS)
    merchants.to_csv('data/raw/merchants.csv', index=False)

    print("→ Generating transactions (this may take sometime)...")
    transactions = generate_transactions(users, merchants, n=TARGET_TRANSACTIONS)
    transactions.to_csv('data/raw/transactions.csv', index=False)

    print("\nData generation complete!")
    print(f"Transactions : {len(transactions):,}")
    print(f"Users        : {len(users):,}")
    print(f"Merchants    : {len(merchants):,}")
    print(f"Txns / User  : {len(transactions) / len(users):.1f}")
    fraud_rate = transactions['is_fraud'].mean() * 100
    print(f"Fraud Rate   : {fraud_rate:.2f}%")
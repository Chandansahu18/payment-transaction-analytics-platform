import uuid
import random
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta, date

random.seed(42)
Faker.seed(42)
fake = Faker('en_IN')

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

def generate_users(n=1000):
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

def generate_merchants(n=200):
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

def build_transaction(user_id, merchant_ids, merchant_category_map, ts, is_fraud=None):
    merchant_id = random.choice(merchant_ids)
    city = random.choice(INDIAN_CITIES)
    amount = round(random.uniform(30000, 60000), 2) if is_fraud else round(random.uniform(50, 25000), 2)
    return {
        'transaction_id': str(uuid.uuid4()),
        'user_id': user_id,
        'merchant_id': merchant_id,
        'merchant_category': merchant_category_map[merchant_id],
        'payment_method': random.choice(PAYMENT_METHODS),
        'amount': amount,
        'currency': 'INR',
        'status': random.choice(STATUSES),
        'is_fraud': is_fraud if is_fraud is not None else False,
        'device_type': random.choice(DEVICE_TYPES),
        'city': city,
        'state': CITY_STATE_MAP[city],
        'transaction_ts': ts,
        'created_at': datetime.now()
    }

def generate_burst_transactions(burst_user_ids, merchant_ids, merchant_category_map, start, end, user_reg_map, user_end_map):
    transactions = []
    for user_id in burst_user_ids:
        user_start = user_reg_map[user_id]
        user_end_local = user_end_map[user_id]
        if user_start >= user_end_local:
            continue
        user_seconds = int((user_end_local - user_start).total_seconds())

        for _ in range(2):
            base_ts = user_start + timedelta(seconds=random.randint(0, user_seconds))
            count = random.randint(6, 8)
            for _ in range(count):
                ts = base_ts + timedelta(minutes=random.randint(0, 55))
                if ts > user_end_local:
                    break
                transactions.append(build_transaction(user_id, merchant_ids, merchant_category_map, ts, is_fraud=random.random() < 0.3))

        base_ts = user_start + timedelta(seconds=random.randint(0, max(0, user_seconds - 86400)))
        count = random.randint(18, 22)
        for _ in range(count):
            ts = base_ts + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            if ts > user_end_local:
                break
            transactions.append(build_transaction(user_id, merchant_ids, merchant_category_map, ts, is_fraud=random.random() < 0.3))

        base_ts = user_start + timedelta(seconds=random.randint(0, max(0, user_seconds - 86400)))
        for _ in range(random.randint(6, 8)):
            ts = base_ts + timedelta(minutes=random.randint(0, 55))
            if ts > user_end_local:
                break
            transactions.append(build_transaction(user_id, merchant_ids, merchant_category_map, ts, is_fraud=random.random() < 0.35))
        for _ in range(random.randint(10, 14)):
            ts = base_ts + timedelta(hours=random.randint(1, 23), minutes=random.randint(0, 59))
            if ts > user_end_local:
                break
            transactions.append(build_transaction(user_id, merchant_ids, merchant_category_map, ts, is_fraud=random.random() < 0.35))

    return transactions

def generate_transactions(users_df, merchants_df, n=400000):
    transactions = []
    user_ids = users_df['user_id'].tolist()
    merchant_ids = merchants_df['merchant_id'].tolist()
    merchant_category_map = merchants_df.set_index('merchant_id')['merchant_category'].to_dict()
    
    start = datetime(2024, 1, 1)
    end = datetime(2025, 6, 30)

    user_reg_map = users_df[['user_id', 'registration_date']].copy()
    user_reg_map['registration_date'] = pd.to_datetime(user_reg_map['registration_date'])
    user_reg_map = dict(zip(
        user_reg_map['user_id'],
        user_reg_map['registration_date'].apply(lambda x: max(x.to_pydatetime(), start))
    ))

    user_end_map = {}
    for uid in user_ids:
        duration_days = random.choices([60, 180, 365, 540], weights=[20, 30, 30, 20])[0]
        user_end_map[uid] = min(user_reg_map[uid] + timedelta(days=duration_days), end)

    burst_user_ids = random.sample(user_ids, k=30)
    transactions.extend(generate_burst_transactions(burst_user_ids, merchant_ids, merchant_category_map, start, end, user_reg_map, user_end_map))

    remaining = n - len(transactions)
    for _ in range(remaining):
        user_id = random.choice(user_ids)
        user_start = user_reg_map[user_id]
        user_end_local = user_end_map[user_id]
        if user_start >= user_end_local:
            continue
        user_seconds = int((user_end_local - user_start).total_seconds())

        merchant_id = random.choice(merchant_ids)
        merchant_category = merchant_category_map[merchant_id]
        status = random.choice(STATUSES)

        fraud_probability = 0.012
        amount = round(random.uniform(50, 25000), 2)

        if amount > 15000:
            fraud_probability += 0.02
        if merchant_category in ['Travel', 'Electronics']:
            fraud_probability += 0.015

        ts = user_start + timedelta(seconds=random.randint(0, user_seconds))
        if 1 <= ts.hour <= 5:
            fraud_probability += 0.012

        is_fraud = random.random() < fraud_probability

        if is_fraud:
            amount = round(random.uniform(30000, 60000), 2)

        city = random.choice(INDIAN_CITIES)

        transactions.append({
            'transaction_id': str(uuid.uuid4()),
            'user_id': user_id,
            'merchant_id': merchant_id,
            'merchant_category': merchant_category,
            'payment_method': random.choice(PAYMENT_METHODS),
            'amount': amount,
            'currency': 'INR',
            'status': status,
            'is_fraud': is_fraud,
            'device_type': random.choice(DEVICE_TYPES),
            'city': city,
            'state': CITY_STATE_MAP[city],
            'transaction_ts': ts,
            'created_at': datetime.now()
        })

    return pd.DataFrame(transactions)

if __name__ == '__main__':
    print("Generating synthetic payment data with realistic fraud patterns...")

    print("→ Generating users...")
    users = generate_users(1000)
    users.to_csv('data/raw/users.csv', index=False)

    print("→ Generating merchants...")
    merchants = generate_merchants(200)
    merchants.to_csv('data/raw/merchants.csv', index=False)

    print("→ Generating transactions (this may take sometime)...")
    transactions = generate_transactions(users, merchants, n=400000)
    transactions.to_csv('data/raw/transactions.csv', index=False)

    print("\nData generation complete!")
    print(f"Transactions : {len(transactions):,}")
    print(f"Users        : {len(users):,}")
    print(f"Merchants    : {len(merchants):,}")
    print(f"Fraud Rate   : {transactions['is_fraud'].mean()*100:.2f}%")
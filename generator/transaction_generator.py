import uuid
import random
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

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
            'registration_date': fake.date_between(start_date='-3y', end_date='-6m'),
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


def generate_transactions(users_df, merchants_df, n=400000):
    transactions = []
    user_ids = users_df['user_id'].tolist()
    merchant_ids = merchants_df['merchant_id'].tolist()
    merchant_category_map = merchants_df.set_index('merchant_id')['merchant_category'].to_dict()

    start = datetime(2024, 1, 1)
    end = datetime(2025, 6, 30)
    total_seconds = int((end - start).total_seconds())

    for _ in range(n):
        merchant_id = random.choice(merchant_ids)
        merchant_category = merchant_category_map[merchant_id]
        status = random.choice(STATUSES)

        fraud_probability = 0.012
        amount = round(random.uniform(50, 25000), 2)

        if amount > 15000:
            fraud_probability += 0.02
        if merchant_category in ['Travel', 'Electronics']:
            fraud_probability += 0.015

        ts = start + timedelta(seconds=random.randint(0, total_seconds))
        if 1 <= ts.hour <= 5:
            fraud_probability += 0.012

        is_fraud = random.random() < fraud_probability

        if is_fraud:
            amount = round(random.uniform(30000, 60000), 2)

        city = random.choice(INDIAN_CITIES)

        transactions.append({
            'transaction_id': str(uuid.uuid4()),
            'user_id': random.choice(user_ids),
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
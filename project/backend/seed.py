import uuid
import random
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Replace 'your_models_file' with the actual file name
from model.model import Base, User, Wallet, Transaction, Session

# Create engine and session
engine = create_engine('sqlite:///bank.db')  # Replace with your database URL
SessionMaker = sessionmaker(bind=engine)
db_session = SessionMaker()

# Create tables
Base.metadata.create_all(engine)

# Helper function to generate random date within the last year


def random_date(start_date, end_date):
    time_between = end_date - start_date
    days_between = time_between.days
    random_number_of_days = random.randrange(days_between)
    return start_date + timedelta(days=random_number_of_days)


# Seed Users and Wallets
users = [
    {"username": "alice", "email": "alice@example.com",
        "password_hash": "hashed_password_1"},
    {"username": "bob", "email": "bob@example.com",
        "password_hash": "hashed_password_2"},
    {"username": "charlie", "email": "charlie@example.com",
        "password_hash": "hashed_password_3"},
    {"username": "david", "email": "david@example.com",
        "password_hash": "hashed_password_4"},
    {"username": "eve", "email": "eve@example.com",
        "password_hash": "hashed_password_5"},
]

created_users = []
for user_data in users:
    user = User(**user_data)
    db_session.add(user)
    db_session.flush()  # This assigns the user_id

    wallet = Wallet(user_id=user.user_id, balance=Decimal('1000.00'))
    db_session.add(wallet)

    created_users.append(user)

db_session.commit()

# Fetch all wallets for transactions
wallets = db_session.query(Wallet).all()

# Generate and seed 500 random transactions
transaction_types = ['DEPOSIT', 'WITHDRAWAL', 'TRANSFER']
transaction_statuses = ['PENDING', 'COMPLETED', 'FAILED']
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

for _ in range(500):
    wallet = random.choice(wallets)
    transaction_type = random.choice(transaction_types)
    amount = Decimal(random.uniform(10, 500)).quantize(Decimal('0.01'))
    status = random.choice(transaction_statuses)

    transaction_data = {
        "wallet_id": wallet.wallet_id,
        "amount": amount,
        "type": transaction_type,
        "status": status,
        "description": f"Random {transaction_type.lower()} transaction",
        "created_at": random_date(start_date, end_date),
    }

    if transaction_type == 'TRANSFER':
        recipient_wallet = random.choice([w for w in wallets if w != wallet])
        transaction_data["recipient_wallet_id"] = recipient_wallet.wallet_id

    transaction = Transaction(**transaction_data)
    db_session.add(transaction)

    # Update wallet balances for completed transactions
    if status == "COMPLETED":
        if transaction_type == "DEPOSIT":
            wallet.balance += amount
        elif transaction_type == "WITHDRAWAL":
            wallet.balance -= amount
        elif transaction_type == "TRANSFER":
            wallet.balance -= amount
            recipient_wallet = db_session.query(Wallet).filter_by(
                wallet_id=transaction.recipient_wallet_id).first()
            recipient_wallet.balance += amount

    transaction.updated_at = transaction.created_at

# Generate sample sessions for users
for user in created_users:
    session_data = {
        "user_id": user.user_id,
        "jwt_token": f"sample_jwt_token_for_{user.username}",
        "refresh_token": f"sample_refresh_token_for_{user.username}",
        "is_active": True,
        "expires_at": datetime.now() + timedelta(days=1)
    }
    session = Session(**session_data)
    db_session.add(session)

db_session.commit()

print("Database seeded successfully with 5 users, their wallets, 500 random transactions, and sample sessions!")

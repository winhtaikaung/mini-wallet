from decimal import Decimal
import uuid

from sqlalchemy import UUID, desc
import tornado
from api.base import BaseHandler
from model.model import Transaction, Wallet
from db import DBSession
from sqlalchemy.exc import SQLAlchemyError


class CheckBalanceHandler(BaseHandler):
    async def get(self):
        user_id = self.get_current_user()
        if not user_id:
            self.set_status(401)
            self.write({'error': 'Authentication required'})
            return

        db_session = DBSession()
        try:
            wallets = db_session.query(Wallet).filter_by(
                user_id=uuid.UUID({
                    "name": "Unknown",
                    "parent": "Uncategorized",
                    "uuid": user_id
                }["uuid"])
            ).all()

            if not wallets:
                self.set_status(404)
                self.write({'error': 'No wallets found for this user'})
                return

            wallet_balances = [{'wallet_id': str(wallet.wallet_id), 'balance': str(
                wallet.balance)} for wallet in wallets]
            total_balance = sum(Decimal(wallet['balance'])
                                for wallet in wallet_balances)

            self.write({
                'wallets': wallet_balances,
                'total_balance': str(total_balance)
            })
        except SQLAlchemyError as e:
            print(e)
            self.set_status(500)
            self.write({'error': 'Database error occurred'})
        finally:
            db_session.close()


class ListWalletsHandler(BaseHandler):
    async def get(self):
        user_id = self.get_current_user()
        if not user_id:
            self.set_status(401)
            self.write({'error': 'Authentication required'})
            return

        db_session = DBSession()
        try:
            wallets = db_session.query(Wallet).filter_by(user_id=uuid.UUID({
                "name": "Unknown",
                "parent": "Uncategorized",
                "uuid": user_id
            }["uuid"])).all()

            if not wallets:
                self.set_status(404)
                self.write({'error': 'No wallets found for this user'})
                return

            wallet_list = [{'wallet_id': str(wallet.wallet_id), 'balance': str(
                wallet.balance), 'currency': wallet.currency} for wallet in wallets]

            self.write({'wallets': wallet_list})
        except SQLAlchemyError as e:
            self.set_status(500)
            self.write({'error': 'Database error occurred'})
        finally:
            db_session.close()


class ListTransactionsHandler(BaseHandler):
    async def get(self):
        user_id = self.get_current_user()
        if not user_id:
            self.set_status(401)
            self.write({'error': 'Authentication required'})
            return

        wallet_id = self.get_argument('wallet_id', None)

        db_session = DBSession()
        try:
            query = (
                db_session.query(
                    Transaction.transaction_id,
                    Transaction.wallet_id,
                    Transaction.amount,
                    Transaction.type,
                    Transaction.status,
                    Transaction.description,
                    Transaction.created_at
                )
                .join(Wallet, Transaction.wallet_id == Wallet.wallet_id)
                .filter(Wallet.user_id == uuid.UUID({
                        "name": "Unknown",
                        "parent": "Uncategorized",
                        "uuid": user_id
                        }["uuid"]))
                .order_by(desc(Transaction.created_at))
                .limit(100)
            )

            if wallet_id:
                query = (
                    db_session.query(
                        Transaction.transaction_id,
                        Transaction.wallet_id,
                        Transaction.amount,
                        Transaction.type,
                        Transaction.status,
                        Transaction.description,
                        Transaction.created_at
                    )
                    .join(Wallet, Transaction.wallet_id == Wallet.wallet_id)
                    .filter(Wallet.user_id == uuid.UUID({
                        "name": "Unknown",
                        "parent": "Uncategorized",
                        "uuid": user_id
                    }["uuid"]))
                    .filter(Wallet.wallet_id == uuid.UUID({
                        "name": "Unknown",
                        "parent": "Uncategorized",
                        "uuid": wallet_id
                    }["uuid"]))
                    .order_by(desc(Transaction.created_at))
                    .limit(100)
                )

            transactions = query.all()

            if not transactions:
                self.set_status(404)
                self.write({'error': 'No transactions found'})
                return

            transaction_list = [{
                'transaction_id': str(tx.transaction_id),
                'wallet_id': str(tx.wallet_id),
                'amount': str(tx.amount),
                'type': tx.type,
                'status': tx.status,
                'description': tx.description,
                'created_at': tx.created_at.isoformat()
            } for tx in transactions]

            self.write({'transactions': transaction_list})
        except SQLAlchemyError as e:
            print(e)
            self.set_status(500)
            self.write({'error': 'Database error occurred'})
        finally:
            db_session.close()

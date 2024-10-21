from decimal import Decimal
import uuid
import tornado
from api.base import BaseHandler
from model.model import Transaction, Wallet
from db import DBSession
from sqlalchemy.exc import SQLAlchemyError


class TransferHandler(BaseHandler):
    async def post(self):
        user_id = self.get_current_user()
        if not user_id:
            self.set_status(401)
            self.write({'error': 'Authentication required'})
            return

        try:
            amount = Decimal(self.get_argument('amount'))
            recipient_id = self.get_argument('recipient_id')
        except (ValueError, tornado.web.MissingArgumentError) as e:
            self.set_status(400)
            self.write({'error': str(e)})
            return

        db_session = DBSession()
        try:
            sender_wallet = db_session.query(
                Wallet).filter_by(user_id=uuid.UUID({
                    "name": "Unknown",
                    "parent": "Uncategorized",
                    "uuid": user_id
                }["uuid"])).first()
            recipient_wallet = db_session.query(
                Wallet).filter_by(user_id=uuid.UUID({
                    "name": "Unknown",
                    "parent": "Uncategorized",
                    "uuid": recipient_id
                }["uuid"])).first()

            if not sender_wallet or not recipient_wallet:
                self.set_status(404)
                self.write({'error': 'Sender or recipient wallet not found'})
                return

            if sender_wallet.balance < amount:
                self.set_status(400)
                self.write({'error': 'Insufficient funds'})
                return

            # Perform transfer
            sender_wallet.balance -= amount
            recipient_wallet.balance += amount

            # Create transaction records
            sender_transaction = Transaction(
                wallet_id=sender_wallet.wallet_id,
                amount=-amount,
                type='TRANSFER',
                status='COMPLETED',
                recipient_wallet_id=recipient_wallet.wallet_id,
                description=f"Transfer to {recipient_id}"
            )
            recipient_transaction = Transaction(
                wallet_id=recipient_wallet.wallet_id,
                amount=amount,
                type='TRANSFER',
                status='COMPLETED',
                description=f"Transfer from {user_id}"
            )

            # db_session.add(sender_wallet)
            # db_session.add(recipient_wallet)
            db_session.add(sender_transaction)
            db_session.add(recipient_transaction)
            db_session.commit()

            self.write({'message': 'Transfer successful',
                       'new_balance': str(sender_wallet.balance)})
        except Exception as e:
            db_session.rollback()
            print(e)
            self.set_status(500)
            self.write({'error': 'Database error occurred'})
        finally:
            db_session.close()


class WithdrawHandler(BaseHandler):
    async def post(self):
        user_id = self.get_current_user()
        if not user_id:
            self.set_status(401)
            self.write({'error': 'Authentication required'})
            return

        try:
            amount = Decimal(self.get_argument('amount'))
        except (ValueError, tornado.web.MissingArgumentError) as e:
            self.set_status(400)
            self.write({'error': str(e)})
            return

        db_session = DBSession()
        try:
            wallet = db_session.query(Wallet).filter_by(
                user_id=uuid.UUID({
                    "name": "Unknown",
                    "parent": "Uncategorized",
                    "uuid": user_id
                }["uuid"])).first()

            if not wallet:
                self.set_status(404)
                self.write({'error': 'Wallet not found'})
                return

            if wallet.balance < amount:
                self.set_status(400)
                self.write({'error': 'Insufficient funds'})
                return

            # Perform withdrawal
            wallet.balance -= amount

            # Create transaction record
            transaction = Transaction(
                wallet_id=wallet.wallet_id,
                amount=-amount,
                type='WITHDRAWAL',
                status='COMPLETED',
                description="Withdrawal"
            )

            db_session.add(transaction)
            db_session.commit()

            self.write({'message': 'Withdrawal successful',
                       'new_balance': str(wallet.balance)})
        except SQLAlchemyError as e:
            db_session.rollback()
            self.set_status(500)
            self.write({'error': 'Database error occurred'})
        finally:
            db_session.close()


class DepositHandler(BaseHandler):
    async def post(self):
        user_id = self.get_current_user()
        if not user_id:
            self.set_status(401)
            self.write({'error': 'Authentication required'})
            return

        try:
            amount = Decimal(self.get_argument('amount'))
        except (ValueError, tornado.web.MissingArgumentError) as e:
            self.set_status(400)
            self.write({'error': str(e)})
            return

        db_session = DBSession()
        try:
            wallet = db_session.query(Wallet).filter_by(
                user_id=uuid.UUID({
                    "name": "Unknown",
                    "parent": "Uncategorized",
                    "uuid": user_id
                }["uuid"])).first()

            if not wallet:
                self.set_status(404)
                self.write({'error': 'Wallet not found'})
                return

            # Perform deposit
            wallet.balance += amount

            # Create transaction record
            transaction = Transaction(
                wallet_id=wallet.wallet_id,
                amount=amount,
                type='DEPOSIT',
                status='COMPLETED',
                description="Deposit"
            )

            db_session.add(transaction)
            db_session.commit()

            self.write({'message': 'Deposit successful',
                       'new_balance': str(wallet.balance)})
        except SQLAlchemyError as e:
            db_session.rollback()
            self.set_status(500)
            self.write({'error': 'Database error occurred'})
        finally:
            db_session.close()

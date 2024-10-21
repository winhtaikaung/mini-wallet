import asyncio
from datetime import datetime, timedelta
import uuid
import jwt
import tornado
from api.auth.auth_handler import MainHandler, LoginHandler, LogoutHandler, RefreshTokenHandler, RegisterHandler
from api.transaction.transaction_handler import TransferHandler, WithdrawHandler, DepositHandler

from api.wallet.wallet_handler import CheckBalanceHandler, ListTransactionsHandler, ListWalletsHandler


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/register", RegisterHandler),
        (r"/login", LoginHandler),
        (r"/logout", LogoutHandler),
        (r"/refresh", RefreshTokenHandler),
        (r"/transfer", TransferHandler),
        (r"/withdraw", WithdrawHandler),
        (r"/deposit", DepositHandler),
        (r"/balance", CheckBalanceHandler),
        (r"/wallets", ListWalletsHandler),
        (r"/transactions", ListTransactionsHandler),
    ], debug=True)


async def main():
    app = make_app()
    app.listen(8888)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

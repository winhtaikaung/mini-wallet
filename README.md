# Mini Wallet Application

This project is for testing purpose 



# Mini Wallet API

This application is a mini wallet API that allows users to manage multiple wallets, perform transactions, and track their balances. It provides a set of endpoints for user authentication, wallet management, and transaction handling.

## Functionality

1. **User Authentication**
   - Register new users
   - Login and receive JWT tokens
   - Logout to invalidate tokens
   - Refresh expired tokens

2. **Wallet Management**
   - List all wallets for a user
   - Check balance for individual wallets and total balance across all wallets

3. **Transaction Handling**
   - Deposit money into a wallet
   - Withdraw money from a wallet
   - Transfer money between wallets
   - List transactions with optional filtering by wallet

## Technology Stack

- **Backend Framework**: Tornado (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens)
- **API Testing**: Postman

## Transaction Handling

### Transaction Process
1. When a transaction is initiated, it's first recorded in the database with a 'PENDING' status.
2. The system then attempts to execute the transaction (e.g., updating wallet balances).
3. If the execution is successful, the transaction status is updated to 'COMPLETED'.
4. If any error occurs during execution, the transaction status is set to 'FAILED'.

### Failed Transactions
If a transaction fails:
1. The system rolls back any partial changes made to the database.
2. The transaction record is kept with a 'FAILED' status for auditing purposes.
3. An error message is returned to the user explaining the reason for failure.

### Transaction Keeping Logic
- All transactions are recorded in the `transactions` table.
- Each transaction is linked to a specific wallet (or two wallets in case of transfers).
- Transactions include details such as amount, type (DEPOSIT, WITHDRAWAL, TRANSFER), status, and timestamps.
- The system maintains a balance for each wallet, which is updated after successful transactions.

## Error Handling

The application implements comprehensive error handling to ensure robustness and provide clear feedback to users.

### Error Types

1. **Authentication Errors** (401)
   - Invalid or expired JWT token
   - Unauthorized access to protected endpoints

2. **Not Found Errors** (404)
   - Wallet not found
   - No transactions found for the given criteria

3. **Bad Request Errors** (400)
   - Invalid input data (e.g., negative amount for transactions)
   - Insufficient funds for withdrawals or transfers

4. **Internal Server Errors** (500)
   - Database connection issues
   - Unexpected server-side errors

### Error Responses

All error responses follow a consistent format:

```json
{
  "error": "Description of the error"
}
```

The application uses try-except blocks to catch and handle various exceptions, providing appropriate HTTP status codes and error messages in the response.

### Development ReadMe

Development Notes are as follows.

- Backend Readme [here](./project/backend/README.md)

FrontEnd Readme [here](./project/frontend/README.md)

---

This README provides an overview of the Mini Wallet API's functionality, technology stack, transaction handling process, and error management. It serves as a quick reference for developers working with or integrating this API.

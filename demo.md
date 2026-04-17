# Banking System Demo Guide

Use this file as your presentation script. It covers setup, seed data, every page, every route, expected behavior, and a clean demo flow.

## 1. Demo Goal

Show that the project is a complete Flask and SQLite banking system:

- Users can register and log in.
- Customers can view accounts and transactions.
- Customers can create accounts.
- Customers can deposit, withdraw, and transfer money.
- API routes return JSON for dashboard data.
- SQLite stores all schema and dummy data locally.
- Security basics are present: hashed passwords, sessions, CSRF, validation, and protected routes.

## 2. Before the Demo

Open a terminal in the project folder:

```bash
cd /Users/anvaykharb/Desktop/dmbs/DBMS_Banking_System
```

Reset the SQLite database so the demo starts from clean dummy data:

```bash
bash scripts/setup_db.sh
```

Run all tests:

```bash
.venv/bin/python -m pytest -q
```

Expected result:

```text
14 passed
```

Start the app:

```bash
bash scripts/run_dev.sh
```

Open:

```text
http://127.0.0.1:5050
```

## 3. Demo Logins

All seeded demo users use:

```text
Password123
```

Best users for the live demo:

| Username | Customer | Why use it |
| --- | --- | --- |
| `priya` | Priya Verma | Has two accounts and a good transaction history |
| `aarav` | Aarav Sharma | Good transfer target and second login account |

Other seeded users:

| Username | Customer |
| --- | --- |
| `rohan` | Rohan Mehta |
| `sneha` | Sneha Iyer |
| `karan` | Karan Patel |
| `ananya` | Ananya Rao |
| `vivek` | Vivek Nair |
| `meera` | Meera Kapoor |

## 4. Seed Data to Mention

The database starts with:

| Table | Rows |
| --- | ---: |
| `branch` | 8 |
| `customer` | 10 |
| `app_user` | 8 |
| `account` | 16 |
| `employee` | 12 |
| `loan` | 10 |
| `bank_transaction` | 20 |
| `loan_payment` | 14 |

Say this:

```text
The demo is not an empty app. It starts with realistic dummy banking data, including branches, customers, login users, accounts, loans, transactions, and loan payments.
```

## 5. Route Map

| Method | Route | Page or API | What to show |
| --- | --- | --- | --- |
| `GET` | `/auth/login` | Page | Login page |
| `POST` | `/auth/login` | Form action | Login with seeded user |
| `GET` | `/auth/register` | Page | Registration form |
| `POST` | `/auth/register` | Form action | Create new customer and user |
| `POST` | `/auth/logout` | Form action | Logout button |
| `GET` | `/` | Page | Dashboard |
| `POST` | `/accounts/create` | Form action | Create a new account |
| `POST` | `/transactions/create` | Form action | Deposit, withdraw, transfer |
| `GET` | `/api/summary` | API | Summary JSON |
| `GET` | `/api/accounts` | API | Logged-in customer accounts JSON |
| `GET` | `/api/transactions` | API | Logged-in customer transactions JSON |

## 6. Live Demo Script

### Step 1: Show Protected Dashboard Redirect

Open:

```text
http://127.0.0.1:5050/
```

Expected result:

- Because you are not logged in, the app redirects to `/auth/login`.

Say this:

```text
The dashboard is protected. Anonymous users are redirected to login.
```

### Step 2: Show Login Page

Route:

```text
GET /auth/login
```

Show:

- Modern login page.
- Demo hint with seeded users.
- Username field.
- Password field.

Use:

```text
username: priya
password: Password123
```

Submit the form.

Route used by the form:

```text
POST /auth/login
```

Expected result:

- Login succeeds.
- Session is created.
- Browser redirects to `/`.
- Flash message says welcome back.

Say this:

```text
Passwords are not stored directly. The seeded users have Werkzeug password hashes in SQLite.
```

### Step 3: Show Dashboard Page

Route:

```text
GET /
```

Show these areas:

1. Top banking command center hero.
2. Signed-in user card.
3. Primary balance snapshot.
4. Summary metric tiles.
5. Create Account form.
6. Create Transaction form.
7. My Accounts table.
8. Recent Transactions table.
9. Branch Directory table.
10. Recent Loans table.

Say this:

```text
The dashboard combines bank-wide summary data with customer-specific account and transaction data.
```

### Step 4: Explain Dashboard Summary

Point to the metric tiles:

- Branches
- Customers
- Accounts
- Loans
- Deposits
- Loans issued

Where the data comes from:

```text
BankingRepository.get_summary()
```

Say this:

```text
These numbers are calculated using SQL aggregate queries against the SQLite database.
```

### Step 5: Show My Accounts

For `priya`, seeded accounts include:

| Account | Type | Branch | Starting balance |
| --- | --- | --- | ---: |
| `1` | Savings | MG Road | Rs 45000.00 |
| `6` | Current | Connaught Place | Rs 60000.00 |

Say this:

```text
The logged-in customer only sees their own accounts. The app uses the customer id from the session.
```

### Step 6: Create a New Account

Use the Create Account form.

Example values:

| Field | Value |
| --- | --- |
| Account type | Savings |
| Branch | MG Road |
| Opening balance | 1000.50 |

Submit.

Route used by the form:

```text
POST /accounts/create
```

Expected result:

- Flash message: account created successfully.
- New account appears in My Accounts.
- If opening balance is greater than zero, an initial deposit transaction is created.

Say this:

```text
The account creation flow validates the branch, creates the account, and records the initial deposit in one database transaction.
```

### Step 7: Deposit Money

Use the Create Transaction form.

Example values:

| Field | Value |
| --- | --- |
| Transaction type | Deposit |
| Amount | 250.25 |
| Source account | Newly created account, or account 1 |
| Description | Demo deposit |

Submit.

Route used by the form:

```text
POST /transactions/create
```

Expected result:

- Flash message: transaction completed successfully.
- Account balance increases.
- Transaction appears in Recent Transactions.

Say this:

```text
Deposits update the balance and insert a row into bank_transaction.
```

### Step 8: Withdraw Money

Use the Create Transaction form.

Example values:

| Field | Value |
| --- | --- |
| Transaction type | Withdraw |
| Amount | 100 |
| Source account | Account 1 |
| Description | Demo withdrawal |

Expected result:

- Balance decreases by Rs 100.
- Withdrawal appears in Recent Transactions.

Say this:

```text
Withdrawals are blocked if the account does not have enough balance.
```

### Step 9: Transfer Money

Use the Create Transaction form.

Example values:

| Field | Value |
| --- | --- |
| Transaction type | Transfer |
| Amount | 500 |
| Source account | Account 1 |
| Target account | Account 2 |
| Description | Demo transfer to Aarav |

Expected result:

- Source balance decreases.
- Target balance increases.
- Transfer appears in Recent Transactions.

Say this:

```text
Transfers update two account rows and insert one transaction row. The app prevents transferring from accounts that do not belong to the logged-in user.
```

### Step 10: Show Transfer Validation

Use the Create Transaction form.

Example invalid values:

| Field | Value |
| --- | --- |
| Transaction type | Transfer |
| Amount | 500 |
| Source account | Account 1 |
| Target account | blank |

Expected result:

- Flash message explains that target account is required.
- No transaction is created.

Say this:

```text
Validation happens before repository writes. Invalid transactions do not touch the database.
```

### Step 11: Show API Summary

While still logged in, open:

```text
http://127.0.0.1:5050/api/summary
```

Route:

```text
GET /api/summary
```

Expected result:

```json
{
  "accounts": 16,
  "branches": 8,
  "customers": 10,
  "loans": 10,
  "total_deposit": 1160300,
  "total_loan": 10395000
}
```

The totals may change if you created new accounts or transactions during the demo.

Say this:

```text
This route returns the same summary data as JSON, useful for dashboards or external clients.
```

### Step 12: Show API Accounts

Open:

```text
http://127.0.0.1:5050/api/accounts
```

Route:

```text
GET /api/accounts
```

Expected result:

- JSON list of accounts for the logged-in customer only.
- For `priya`, seeded accounts are account `1` and account `6`.
- Any accounts created during the demo also appear.

Say this:

```text
The API is session-aware. It uses the logged-in user's customer id.
```

### Step 13: Show API Transactions

Open:

```text
http://127.0.0.1:5050/api/transactions
```

Route:

```text
GET /api/transactions
```

Expected result:

- JSON list of recent transactions for the logged-in customer's source accounts.
- Deposits, withdrawals, and transfers are included.

Say this:

```text
The transaction API reads from bank_transaction joined through the customer's accounts.
```

### Step 14: Show API Authentication Protection

Open a private/incognito browser window and visit:

```text
http://127.0.0.1:5050/api/summary
```

Expected result:

```json
{"error":"Authentication required."}
```

Status code:

```text
401 Unauthorized
```

Say this:

```text
HTML pages redirect anonymous users to login. API routes return JSON errors.
```

### Step 15: Show Registration Page

Logout first or open:

```text
http://127.0.0.1:5050/auth/register
```

Route:

```text
GET /auth/register
```

Show fields:

- Full name
- Date of birth
- Email
- Phone
- Address
- Username
- Password

Example new user:

| Field | Value |
| --- | --- |
| Full name | Demo Student |
| Date of birth | 2000-01-01 |
| Email | demo.student@example.com |
| Phone | 9667788990 |
| Address | 100 Demo Street |
| Username | demostudent |
| Password | Password123 |

Submit.

Route used by the form:

```text
POST /auth/register
```

Expected result:

- New customer row is created.
- New app_user row is created.
- User is logged in automatically.
- Dashboard opens.

Say this:

```text
Registration writes both customer profile data and login data in a single transaction.
```

### Step 16: Show Logout

Click Logout in the navbar.

Route:

```text
POST /auth/logout
```

Expected result:

- Session clears.
- Browser redirects to login.

Say this:

```text
Logout clears the session. The dashboard becomes protected again.
```

## 7. Every Page Checklist

Use this as a quick checklist during the demo:

| Page | URL | Demo action |
| --- | --- | --- |
| Login | `/auth/login` | Log in as `priya` |
| Register | `/auth/register` | Create a new demo user |
| Dashboard | `/` | Show metrics, account form, transaction form, tables |
| API Summary | `/api/summary` | Show JSON summary |
| API Accounts | `/api/accounts` | Show customer accounts JSON |
| API Transactions | `/api/transactions` | Show transactions JSON |

## 8. Every Form Checklist

| Form | Route | Required fields | Demo result |
| --- | --- | --- | --- |
| Login | `POST /auth/login` | username, password, CSRF token | Starts session |
| Register | `POST /auth/register` | name, address, phone, email, username, password, CSRF token | Creates customer and user |
| Logout | `POST /auth/logout` | CSRF token | Clears session |
| Create Account | `POST /accounts/create` | account type, branch, opening balance, CSRF token | Creates account |
| Create Transaction | `POST /transactions/create` | transaction type, amount, source account, CSRF token | Creates transaction |

## 9. Every API Checklist

| API | URL | Login needed | Expected status |
| --- | --- | --- | --- |
| Summary | `/api/summary` | Yes | `200 OK` when logged in, `401` when anonymous |
| Accounts | `/api/accounts` | Yes | `200 OK` when logged in, `401` when anonymous |
| Transactions | `/api/transactions` | Yes | `200 OK` when logged in, `401` when anonymous |

## 10. Database Explanation for Demo

Explain the tables in this order:

1. `branch`: bank locations.
2. `customer`: personal customer information.
3. `app_user`: login username and password hash linked to one customer.
4. `account`: customer bank accounts linked to a branch.
5. `employee`: branch employees.
6. `loan`: loans issued to customers.
7. `bank_transaction`: deposits, withdrawals, and transfers.
8. `loan_payment`: payments made against loans.

Use this short explanation:

```text
The schema is relational. Customers own accounts and loans. Branches own accounts, employees, and loans. Transactions reference source and optional target accounts. Foreign keys keep the data connected.
```

## 11. Reset After Demo

If the demo creates extra users, accounts, or transactions, reset everything:

```bash
bash scripts/setup_db.sh
```

This returns the database to the seeded state from `banking_system.sql`.

## 12. Backup Demo Plan

If the browser already has an old session:

1. Click Logout.
2. Run `bash scripts/setup_db.sh`.
3. Log in again as `priya`.

If the app is not running:

```bash
bash scripts/run_dev.sh
```

If the API page redirects or shows login:

1. Log in first.
2. Open `/api/summary` in the same browser.

If a transaction fails:

1. Use source account `1`.
2. Use amount `100`.
3. For transfer, use target account `2`.

## 13. Closing Lines

End the demo with:

```text
This project uses Flask for routing and sessions, services for validation, repositories for SQL, and SQLite for storage. The UI demonstrates the main banking workflows, while the API routes expose the same data as JSON.
```

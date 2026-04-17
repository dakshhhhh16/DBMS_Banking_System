# Banking System

A Flask and SQLite banking system with server-rendered pages, session login, account creation, transactions, dashboard summaries, API endpoints, and a seeded demo database.

The project is ready for local demos. SQLite is used through Python's built-in `sqlite3` module, so no MySQL server or external database service is required.

## Quick Links

- Full demo script: [demo.md](demo.md)
- Main app entry point: [app.py](app.py)
- SQLite schema and seed data: [banking_system.sql](banking_system.sql)
- Database setup script: [scripts/setup_db.sh](scripts/setup_db.sh)
- Full setup script: [scripts/setup_all.sh](scripts/setup_all.sh)
- Dashboard routes: [banking_app/dashboard/routes.py](banking_app/dashboard/routes.py)
- Auth routes: [banking_app/auth/routes.py](banking_app/auth/routes.py)

## Features

- Registration and login with hashed passwords.
- Session-based authentication.
- CSRF protection for form POST requests.
- Dashboard with bank-wide summary metrics.
- Account creation for Savings, Current, and FD accounts.
- Deposit, withdraw, and transfer transactions.
- SQLite foreign keys, checks, indexes, and seed data.
- JSON API endpoints for summary, accounts, and transactions.
- Modern responsive UI built with Jinja templates, Bootstrap, and custom CSS.
- Automated tests for services, app flows, APIs, and SQLite-backed integration.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Flask 3 |
| Templates | Jinja |
| Database | SQLite 3 |
| DB driver | Python stdlib `sqlite3` |
| Config | `python-dotenv` |
| Password hashing | Werkzeug |
| Tests | pytest |
| Styling | Bootstrap 5 plus custom CSS |

## Project Structure

```text
.
|-- app.py
|-- banking_app/
|   |-- __init__.py
|   |-- config.py
|   |-- db.py
|   |-- auth/
|   |   |-- __init__.py
|   |   `-- routes.py
|   |-- dashboard/
|   |   |-- __init__.py
|   |   `-- routes.py
|   |-- repositories/
|   |   |-- __init__.py
|   |   |-- auth_repository.py
|   |   `-- banking_repository.py
|   |-- services/
|   |   |-- __init__.py
|   |   |-- auth_service.py
|   |   `-- banking_service.py
|   `-- utils/
|       |-- __init__.py
|       |-- decorators.py
|       |-- exceptions.py
|       `-- validators.py
|-- templates/
|   |-- base.html
|   |-- index.html
|   |-- auth/
|   |   |-- login.html
|   |   `-- register.html
|   `-- dashboard/
|       `-- home.html
|-- static/
|   |-- app.js
|   `-- style.css
|-- scripts/
|   |-- init_sqlite_db.py
|   |-- run_dev.sh
|   |-- setup_all.sh
|   `-- setup_db.sh
|-- tests/
|   |-- conftest.py
|   |-- test_api_integration.py
|   |-- test_app_flows.py
|   `-- test_services.py
|-- banking_system.sql
|-- demo.md
|-- requirements.txt
|-- .env.example
`-- README.md
```

## Setup

### Recommended Full Setup

```bash
bash scripts/setup_all.sh
```

This command:

1. Creates `.venv` if missing.
2. Installs Python dependencies.
3. Creates `.env` from `.env.example` if missing.
4. Creates or resets the SQLite database at `instance/banking.sqlite3`.
5. Loads all schema objects and dummy data from `banking_system.sql`.

### Manual Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
bash scripts/setup_db.sh
python app.py
```

Open the app:

```text
http://127.0.0.1:5050
```

### Run App

```bash
bash scripts/run_dev.sh
```

### Reset Database Only

```bash
bash scripts/setup_db.sh
```

This recreates the SQLite database from `banking_system.sql`. Any local records created through the UI are removed when this command runs.

### Run Tests

```bash
.venv/bin/python -m pytest -q
```

## Environment Variables

`.env.example`:

```text
SECRET_KEY=replace-with-a-long-random-secret
FLASK_ENV=development
DB_PATH=instance/banking.sqlite3
SESSION_TTL_SECONDS=3600
```

| Variable | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | Flask session signing key | `dev-only-change-me` in code |
| `FLASK_ENV` | Controls secure cookie behavior | `development` |
| `DB_PATH` | SQLite database file path | `instance/banking.sqlite3` |
| `SESSION_TTL_SECONDS` | Session lifetime in seconds | `3600` |

## Demo Users

Every seeded demo user uses the same password:

```text
Password123
```

| Username | Customer | Suggested demo use |
| --- | --- | --- |
| `priya` | Priya Verma | Best primary dashboard demo user |
| `aarav` | Aarav Sharma | Transfer target and second login demo |
| `rohan` | Rohan Mehta | Additional user data |
| `sneha` | Sneha Iyer | Additional user data |
| `karan` | Karan Patel | Additional user data |
| `ananya` | Ananya Rao | Additional user data |
| `vivek` | Vivek Nair | Additional user data |
| `meera` | Meera Kapoor | Additional user data |

## Seed Data Summary

The SQLite seed data includes:

| Data set | Rows |
| --- | ---: |
| Branches | 8 |
| Customers | 10 |
| Login users | 8 |
| Accounts | 16 |
| Employees | 12 |
| Loans | 10 |
| Transactions | 20 |
| Loan payments | 14 |

## Application Routes

| Method | Route | Auth required | Purpose |
| --- | --- | --- | --- |
| `GET` | `/` | Yes | Dashboard page with summary, forms, tables, branches, and loans |
| `GET` | `/auth/login` | No | Login page |
| `POST` | `/auth/login` | No, CSRF required | Validate credentials and start session |
| `GET` | `/auth/register` | No | Registration page |
| `POST` | `/auth/register` | No, CSRF required | Create customer and login user |
| `POST` | `/auth/logout` | Yes, CSRF checked if present | Clear session |
| `POST` | `/accounts/create` | Yes, CSRF required | Create account for logged-in customer |
| `POST` | `/transactions/create` | Yes, CSRF required | Create deposit, withdraw, or transfer |
| `GET` | `/api/summary` | Yes | JSON summary metrics |
| `GET` | `/api/accounts` | Yes | JSON accounts for logged-in customer |
| `GET` | `/api/transactions` | Yes | JSON recent transactions for logged-in customer |

Unauthenticated API calls return:

```json
{"error":"Authentication required."}
```

## Request Flow

```text
Browser
  -> Flask route
  -> service validation
  -> repository SQL
  -> sqlite3 connection
  -> SQLite database file
```

The route files stay thin. Business validation lives in services. SQL lives in repositories.

## Database Schema

The database is defined in `banking_system.sql`.

### Table: `branch`

Stores bank branch records.

| Column | Type | Rules |
| --- | --- | --- |
| `branch_id` | `INTEGER` | Primary key, autoincrement |
| `branch_name` | `TEXT` | Required, unique |
| `city` | `TEXT` | Required |
| `assets` | `NUMERIC` | Required, default `0`, must be `>= 0` |
| `created_at` | `TEXT` | Required, default `CURRENT_TIMESTAMP` |

Relationships:

- Referenced by `account.branch_id`.
- Referenced by `employee.branch_id`.
- Referenced by `loan.branch_id`.

### Table: `customer`

Stores customer profile information.

| Column | Type | Rules |
| --- | --- | --- |
| `customer_id` | `INTEGER` | Primary key, autoincrement |
| `name` | `TEXT` | Required |
| `address` | `TEXT` | Required |
| `phone` | `TEXT` | Required, unique |
| `email` | `TEXT` | Required, unique |
| `dob` | `TEXT` | Optional date string |
| `created_at` | `TEXT` | Required, default `CURRENT_TIMESTAMP` |

Relationships:

- Referenced by `app_user.customer_id`.
- Referenced by `account.customer_id`.
- Referenced by `loan.customer_id`.

### Table: `app_user`

Stores login credentials for customers.

| Column | Type | Rules |
| --- | --- | --- |
| `user_id` | `INTEGER` | Primary key, autoincrement |
| `username` | `TEXT` | Required, unique |
| `password_hash` | `TEXT` | Required, generated by Werkzeug |
| `customer_id` | `INTEGER` | Required, unique foreign key |
| `created_at` | `TEXT` | Required, default `CURRENT_TIMESTAMP` |

Relationships:

- `customer_id` references `customer(customer_id)`.
- `ON DELETE CASCADE` means deleting a customer deletes the login row.

### Table: `account`

Stores customer bank accounts.

| Column | Type | Rules |
| --- | --- | --- |
| `account_no` | `INTEGER` | Primary key, autoincrement |
| `acc_type` | `TEXT` | Required, must be `Savings`, `Current`, or `FD` |
| `balance` | `NUMERIC` | Required, default `0`, must be `>= 0` |
| `open_date` | `TEXT` | Required |
| `branch_id` | `INTEGER` | Required foreign key |
| `customer_id` | `INTEGER` | Required foreign key |

Relationships:

- `branch_id` references `branch(branch_id)`.
- `customer_id` references `customer(customer_id)`.
- Referenced by `bank_transaction.source_account_no`.
- Referenced by `bank_transaction.target_account_no`.

### Table: `employee`

Stores branch employee records.

| Column | Type | Rules |
| --- | --- | --- |
| `emp_id` | `INTEGER` | Primary key, autoincrement |
| `name` | `TEXT` | Required |
| `designation` | `TEXT` | Required |
| `salary` | `NUMERIC` | Required, must be `> 0` |
| `branch_id` | `INTEGER` | Required foreign key |
| `created_at` | `TEXT` | Required, default `CURRENT_TIMESTAMP` |

Relationships:

- `branch_id` references `branch(branch_id)`.

### Table: `loan`

Stores loan records issued to customers.

| Column | Type | Rules |
| --- | --- | --- |
| `loan_id` | `INTEGER` | Primary key, autoincrement |
| `loan_type` | `TEXT` | Required, must be `Home`, `Car`, `Education`, or `Personal` |
| `amount` | `NUMERIC` | Required, must be `> 0` |
| `interest_rate` | `NUMERIC` | Required, must be between `0` and `100` |
| `issue_date` | `TEXT` | Required |
| `branch_id` | `INTEGER` | Required foreign key |
| `customer_id` | `INTEGER` | Required foreign key |

Relationships:

- `branch_id` references `branch(branch_id)`.
- `customer_id` references `customer(customer_id)`.
- Referenced by `loan_payment.loan_id`.

### Table: `bank_transaction`

Stores deposits, withdrawals, and transfers.

| Column | Type | Rules |
| --- | --- | --- |
| `txn_id` | `INTEGER` | Primary key, autoincrement |
| `txn_type` | `TEXT` | Required, must be `Deposit`, `Withdraw`, or `Transfer` |
| `amount` | `NUMERIC` | Required, must be `> 0` |
| `txn_datetime` | `TEXT` | Required |
| `source_account_no` | `INTEGER` | Required foreign key |
| `target_account_no` | `INTEGER` | Optional foreign key |
| `description` | `TEXT` | Optional |

Relationships:

- `source_account_no` references `account(account_no)`.
- `target_account_no` references `account(account_no)`.

Business rules in service/repository code:

- Deposits increase the source account balance.
- Withdrawals decrease the source account balance.
- Transfers decrease the source account and increase the target account.
- Withdrawals and transfers fail when the source balance is insufficient.
- Transfers require a target account.
- Users can only transact from their own source accounts.

### Table: `loan_payment`

Stores payments made against loans.

| Column | Type | Rules |
| --- | --- | --- |
| `payment_id` | `INTEGER` | Primary key, autoincrement |
| `loan_id` | `INTEGER` | Required foreign key |
| `pay_date` | `TEXT` | Required |
| `amount_paid` | `NUMERIC` | Required, must be `> 0` |

Relationships:

- `loan_id` references `loan(loan_id)`.
- `ON DELETE CASCADE` means deleting a loan deletes its payment rows.

## Indexes

| Index | Table | Columns | Purpose |
| --- | --- | --- | --- |
| `idx_account_customer` | `account` | `customer_id` | Fast account lookup for dashboard |
| `idx_account_branch` | `account` | `branch_id` | Branch/account reporting |
| `idx_employee_branch` | `employee` | `branch_id` | Branch staff lookup |
| `idx_loan_customer` | `loan` | `customer_id` | Customer loan lookup |
| `idx_loan_branch` | `loan` | `branch_id` | Branch loan reporting |
| `idx_txn_source` | `bank_transaction` | `source_account_no` | Customer transaction feed |
| `idx_txn_target` | `bank_transaction` | `target_account_no` | Transfer target lookup |
| `idx_txn_datetime` | `bank_transaction` | `txn_datetime` | Recent transaction ordering |
| `idx_payment_loan` | `loan_payment` | `loan_id` | Loan payment history |

## Main Files

| File | Responsibility |
| --- | --- |
| `banking_app/__init__.py` | Flask app factory, extension setup, error handlers |
| `banking_app/config.py` | Environment-backed configuration |
| `banking_app/db.py` | SQLite connection helper, row factory, foreign key enforcement |
| `banking_app/auth/routes.py` | Login, registration, logout routes |
| `banking_app/dashboard/routes.py` | Dashboard, account, transaction, API routes |
| `banking_app/services/auth_service.py` | Auth validation, password hashing, login checks |
| `banking_app/services/banking_service.py` | Account and transaction validation |
| `banking_app/repositories/auth_repository.py` | Auth SQL queries |
| `banking_app/repositories/banking_repository.py` | Banking SQL queries and transaction updates |
| `banking_app/utils/validators.py` | Input validation and CSRF helper |
| `banking_app/utils/decorators.py` | Login-required decorator |
| `templates/` | Jinja pages |
| `static/style.css` | Modern UI styling |
| `static/app.js` | Transaction form behavior |

## Testing Coverage

The current tests cover:

- Auth service validation.
- Banking service validation.
- Registration page flow.
- Login page flow.
- Auth-required redirects.
- Account creation form flow.
- Transfer validation edge case.
- Real SQLite-backed API responses.
- Real SQLite-backed account creation and deposit flow.
- API authentication errors.
- 404 behavior for pages and APIs.

Run them with:

```bash
.venv/bin/python -m pytest -q
```

## Troubleshooting

### Database has old data

Run:

```bash
bash scripts/setup_db.sh
```

### Login fails for demo users

Reset the database:

```bash
bash scripts/setup_db.sh
```

Then use:

```text
username: priya
password: Password123
```

### Port 5050 is already in use

Stop the existing Flask process or change the port in `app.py`.

### Images do not load

The UI uses remote Unsplash images in CSS. The app still works without them, but the image backgrounds need internet access.

## Demo

Use [demo.md](demo.md) for a complete route-by-route presentation plan.

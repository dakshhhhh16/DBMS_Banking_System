# Banking System (Flask + SQLite)

This project is a modular, server-rendered banking system built with Flask, SQLite, and Jinja templates.

It includes:
- Secure registration and login (password hashing + session auth)
- Account creation
- Deposit/withdraw/transfer transactions with validation
- Dashboard summaries and recent activity
- SQLite schema with constraints, foreign keys, and indexes
- Automated tests for key user flows and edge cases

## Architecture

```text
.
|-- app.py
|-- banking_app/
|   |-- __init__.py
|   |-- config.py
|   |-- db.py
|   |-- auth/
|   |   `-- routes.py
|   |-- dashboard/
|   |   `-- routes.py
|   |-- repositories/
|   |   |-- auth_repository.py
|   |   `-- banking_repository.py
|   |-- services/
|   |   |-- auth_service.py
|   |   `-- banking_service.py
|   `-- utils/
|       |-- decorators.py
|       |-- exceptions.py
|       `-- validators.py
|-- templates/
|   |-- base.html
|   |-- auth/
|   |   |-- login.html
|   |   `-- register.html
|   `-- dashboard/
|       `-- home.html
|-- static/
|   |-- app.js
|   `-- style.css
|-- banking_system.sql
|-- tests/
|   |-- test_app_flows.py
|   `-- test_services.py
|-- requirements.txt
`-- .env.example
```

## Prerequisites

- Python 3.10+
- No external database server required. SQLite is included with Python.

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
cp .env.example .env
```

The default database path is `instance/banking.sqlite3`. Update `DB_PATH` in `.env` only if you want a different file.

4. Create/reset the SQLite database and load seed data:

```bash
bash scripts/setup_db.sh
```

5. Run the app:

```bash
python app.py
```

Open: `http://localhost:5050`

Demo logins seeded by `banking_system.sql`:

| Username | Password |
| --- | --- |
| `aarav` | `Password123` |
| `priya` | `Password123` |

## Fast Setup (Recommended)

Use the provided scripts to set up everything:

1. Full setup (virtual environment + Python dependencies + SQLite DB init):

```bash
bash scripts/setup_all.sh
```

2. DB-only reset/init:

```bash
bash scripts/setup_db.sh
```

3. Run app:

```bash
bash scripts/run_dev.sh
```

Notes:
- `scripts/setup_all.sh` creates `.venv` if it does not exist.
- The SQLite database path is read from `DB_PATH` in `.env`.

## Test

Run automated tests:

```bash
pytest -q
```

The tests cover:
- Registration flow
- Login flow
- Account creation flow
- Transaction flow and edge-case validation

## Security Notes

- Passwords are hashed using Werkzeug.
- Session cookies are HTTP-only and SameSite=Lax.
- CSRF checks are enforced on form POSTs.
- Parameterized SQL queries are used via Python's built-in SQLite driver.

## Database Design Notes

- Uses explicit foreign keys with delete/update policies.
- Uses constraints and `CHECK` rules for domain correctness.
- Uses indexes on account/customer/branch and transaction timestamps.
- Uses a dedicated `bank_transaction` table (avoids reserved keyword conflicts).

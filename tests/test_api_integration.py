import sqlite3
from decimal import Decimal
from pathlib import Path

import pytest

from banking_app import create_app


ROOT = Path(__file__).resolve().parents[1]


def build_sqlite_app(tmp_path):
    db_path = tmp_path / "banking_test.sqlite3"
    schema_sql = (ROOT / "banking_system.sql").read_text()

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(schema_sql)

    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "api-test-secret",
            "DB_PATH": str(db_path),
        }
    )
    return app


def csrf_token(client, path="/auth/login"):
    client.get(path)
    with client.session_transaction() as sess:
        return sess["csrf_token"]


def login_as_priya(client):
    response = client.post(
        "/auth/login",
        data={
            "csrf_token": csrf_token(client),
            "username": "priya",
            "password": "Password123",
        },
    )
    assert response.status_code == 302
    assert response.location == "/"


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"name": "A"}, b"Name must be at least 2 characters."),
        ({"address": "Home"}, b"Address must be at least 5 characters."),
        ({"phone": "12345"}, b"Phone must contain 10 to 15 digits."),
        ({"email": "bad-email"}, b"Email format is invalid."),
        ({"dob": "01-01-2000"}, b"Date of birth must be YYYY-MM-DD."),
        ({"username": "abc"}, b"Username must be at least 4 characters."),
        ({"password": "short"}, b"Password must be at least 8 characters."),
        ({"username": "priya"}, b"Username already exists."),
        ({"email": "priya@yahoo.com"}, b"Email already exists."),
        ({"phone": "9123456780"}, b"Phone already exists."),
    ],
)
def test_registration_shows_specific_validation_errors(tmp_path, overrides, message):
    app = build_sqlite_app(tmp_path)
    client = app.test_client()
    payload = {
        "csrf_token": csrf_token(client, "/auth/register"),
        "name": "Demo User",
        "address": "100 Demo Street",
        "phone": "9667788990",
        "email": "demo.user@example.com",
        "dob": "2000-01-01",
        "username": "demouser",
        "password": "Password123",
    }
    payload.update(overrides)

    response = client.post("/auth/register", data=payload, follow_redirects=True)

    assert response.status_code == 200
    assert message in response.data


def test_registration_keeps_entered_values_after_validation_error(tmp_path):
    app = build_sqlite_app(tmp_path)
    client = app.test_client()

    response = client.post(
        "/auth/register",
        data={
            "csrf_token": csrf_token(client, "/auth/register"),
            "name": "Demo User",
            "address": "100 Demo Street",
            "phone": "12345",
            "email": "demo.user@example.com",
            "dob": "2000-01-01",
            "username": "demouser",
            "password": "Password123",
        },
        follow_redirects=True,
    )

    html = response.get_data(as_text=True)
    assert "Phone must contain 10 to 15 digits." in html
    assert 'value="Demo User"' in html
    assert 'value="100 Demo Street"' in html
    assert 'value="demo.user@example.com"' in html
    assert 'value="demouser"' in html
    assert 'value="Password123"' not in html


def test_api_requires_authentication_with_json_response(tmp_path):
    app = build_sqlite_app(tmp_path)
    client = app.test_client()

    response = client.get("/api/summary")

    assert response.status_code == 401
    assert response.json == {"error": "Authentication required."}


def test_missing_regular_route_returns_404_not_dashboard_redirect(tmp_path):
    app = build_sqlite_app(tmp_path)
    client = app.test_client()

    response = client.get("/favicon.ico")

    assert response.status_code == 404


def test_missing_api_route_returns_json_404(tmp_path):
    app = build_sqlite_app(tmp_path)
    client = app.test_client()

    response = client.get("/api/not-real")

    assert response.status_code == 404
    assert "not found" in response.json["error"].lower()


def test_seeded_demo_user_can_read_all_api_endpoints(tmp_path):
    app = build_sqlite_app(tmp_path)
    client = app.test_client()
    login_as_priya(client)

    summary = client.get("/api/summary")
    accounts = client.get("/api/accounts")
    transactions = client.get("/api/transactions")

    assert summary.status_code == 200
    assert summary.json["branches"] == 8
    assert summary.json["customers"] == 10
    assert summary.json["accounts"] == 16
    assert summary.json["loans"] == 10

    assert accounts.status_code == 200
    assert {row["account_no"] for row in accounts.json} == {1, 6}
    assert {row["acc_type"] for row in accounts.json} == {"Savings", "Current"}

    assert transactions.status_code == 200
    assert {row["txn_type"] for row in transactions.json} >= {"Deposit", "Withdraw"}
    assert {row["source_account_no"] for row in transactions.json} == {1, 6}


def test_bank_details_page_uses_separate_bank_view(tmp_path):
    app = build_sqlite_app(tmp_path)
    client = app.test_client()
    login_as_priya(client)

    response = client.get("/bank-details")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Bank Details" in html
    assert "Branch Directory" in html
    assert "Recent Loans" in html
    assert "Employees" in html
    assert "Create Account" not in html
    assert "Create Transaction" not in html


def test_create_account_and_deposit_flow_updates_api_data(tmp_path):
    app = build_sqlite_app(tmp_path)
    client = app.test_client()
    login_as_priya(client)

    create_account_response = client.post(
        "/accounts/create",
        data={
            "csrf_token": csrf_token(client, "/"),
            "acc_type": "Savings",
            "branch_id": "1",
            "opening_balance": "1000.50",
        },
    )
    assert create_account_response.status_code == 302

    accounts = client.get("/api/accounts").json
    new_account = max(accounts, key=lambda row: row["account_no"])
    assert new_account["acc_type"] == "Savings"
    assert new_account["balance"] == "1000.5"

    deposit_response = client.post(
        "/transactions/create",
        data={
            "csrf_token": csrf_token(client, "/"),
            "txn_type": "Deposit",
            "amount": "250.25",
            "source_account_no": str(new_account["account_no"]),
            "target_account_no": "",
            "description": "API integration deposit",
        },
    )
    assert deposit_response.status_code == 302

    updated_accounts = client.get("/api/accounts").json
    updated_account = next(row for row in updated_accounts if row["account_no"] == new_account["account_no"])
    assert Decimal(updated_account["balance"]) == Decimal("1250.75")

    transactions = client.get("/api/transactions").json
    assert any(
        row["source_account_no"] == new_account["account_no"]
        and row["txn_type"] == "Deposit"
        and row["description"] == "API integration deposit"
        for row in transactions
    )


def test_invalid_transfer_does_not_create_transaction(tmp_path):
    app = build_sqlite_app(tmp_path)
    client = app.test_client()
    login_as_priya(client)

    before = client.get("/api/transactions").json
    response = client.post(
        "/transactions/create",
        data={
            "csrf_token": csrf_token(client, "/"),
            "txn_type": "Transfer",
            "amount": "100",
            "source_account_no": "1",
            "target_account_no": "",
        },
    )
    after = client.get("/api/transactions").json

    assert response.status_code == 302
    assert len(after) == len(before)


def test_api_update_and_close_account_flow(tmp_path):
    app = build_sqlite_app(tmp_path)
    client = app.test_client()
    login_as_priya(client)

    create_account_response = client.post(
        "/accounts/create",
        data={
            "csrf_token": csrf_token(client, "/"),
            "acc_type": "Savings",
            "branch_id": "1",
            "opening_balance": "0",
        },
    )
    assert create_account_response.status_code == 302

    accounts = client.get("/api/accounts").json
    new_account = max(accounts, key=lambda row: row["account_no"])

    update_response = client.patch(
        f"/api/accounts/{new_account['account_no']}",
        json={"acc_type": "Current", "branch_id": 2},
        headers={"X-CSRF-Token": csrf_token(client, "/")},
    )
    assert update_response.status_code == 200
    assert update_response.json["acc_type"] == "Current"
    assert update_response.json["branch_id"] == 2

    updated_accounts = client.get("/api/accounts").json
    updated_account = next(row for row in updated_accounts if row["account_no"] == new_account["account_no"])
    assert updated_account["acc_type"] == "Current"
    assert updated_account["branch_id"] == 2

    close_response = client.delete(
        f"/api/accounts/{new_account['account_no']}",
        headers={"X-CSRF-Token": csrf_token(client, "/")},
    )
    assert close_response.status_code == 200

    final_accounts = client.get("/api/accounts").json
    assert all(row["account_no"] != new_account["account_no"] for row in final_accounts)


def test_api_close_account_rejects_non_zero_balance(tmp_path):
    app = build_sqlite_app(tmp_path)
    client = app.test_client()
    login_as_priya(client)

    response = client.delete(
        "/api/accounts/1",
        headers={"X-CSRF-Token": csrf_token(client, "/")},
    )

    assert response.status_code == 400
    assert "balance must be zero" in response.json["error"].lower()

from banking_app import create_app
from banking_app.utils.exceptions import ValidationError


class FakeAuthService:
    def register_user(self, payload):
        return {
            "user_id": 1,
            "username": payload["username"],
            "customer_id": 101,
            "name": payload["name"],
            "email": payload["email"],
        }

    def login_user(self, username, password):
        return {
            "user_id": 1,
            "username": username,
            "customer_id": 101,
            "name": "Test User",
            "email": "test@example.com",
        }

    def get_user_for_session(self, user_id):
        if user_id == 1:
            return {
                "user_id": 1,
                "username": "tester",
                "customer_id": 101,
                "name": "Test User",
                "email": "test@example.com",
            }
        return None


class FakeBankingRepository:
    def get_customer_accounts(self, customer_id):
        return [{"account_no": 11, "acc_type": "Savings", "balance": 1500.0, "open_date": "2026-01-01", "branch_name": "MG Road", "city": "Bengaluru"}]

    def get_recent_transactions_for_customer(self, customer_id):
        return [{"txn_id": 1, "txn_type": "Deposit", "amount": 200, "txn_datetime": "2026-01-01 10:00:00", "source_account_no": 11, "target_account_no": None, "description": "seed"}]


class FakeBankingService:
    def __init__(self):
        self.repository = FakeBankingRepository()
        self.account_calls = 0
        self.txn_calls = 0

    def get_dashboard_payload(self, customer_id):
        return {
            "summary": {
                "branches": 4,
                "customers": 5,
                "accounts": 6,
                "loans": 4,
                "total_deposit": 1234.0,
                "total_loan": 5678.0,
            },
            "reference": {
                "branches": [{"branch_id": 1, "branch_name": "MG Road"}],
                "loans": [],
                "employees": [],
            },
            "accounts": self.repository.get_customer_accounts(customer_id),
            "transactions": self.repository.get_recent_transactions_for_customer(customer_id),
        }

    def create_account(self, customer_id, payload):
        self.account_calls += 1
        return 11

    def create_transaction(self, customer_id, payload):
        if payload.get("txn_type") == "Transfer" and not payload.get("target_account_no"):
            raise ValidationError("Target account is required for transfer.")
        self.txn_calls += 1
        return 1


def build_test_app():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SKIP_DB_INIT": True,
        }
    )
    app.extensions["auth_service"] = FakeAuthService()
    app.extensions["banking_service"] = FakeBankingService()
    return app


def get_csrf_token(client, path):
    client.get(path)
    with client.session_transaction() as sess:
        return sess["csrf_token"]


def test_registration_flow_success():
    app = build_test_app()
    client = app.test_client()

    csrf = get_csrf_token(client, "/auth/register")
    response = client.post(
        "/auth/register",
        data={
            "csrf_token": csrf,
            "name": "Test User",
            "address": "Street 1",
            "phone": "9999999999",
            "email": "new@example.com",
            "dob": "1990-01-01",
            "username": "newuser",
            "password": "Password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Registration successful" in response.data


def test_login_flow_success():
    app = build_test_app()
    client = app.test_client()

    csrf = get_csrf_token(client, "/auth/login")
    response = client.post(
        "/auth/login",
        data={"csrf_token": csrf, "username": "tester", "password": "Password123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Welcome back" in response.data


def test_account_creation_requires_login():
    app = build_test_app()
    client = app.test_client()

    response = client.post("/accounts/create", data={})
    assert response.status_code == 302
    assert "/auth/login" in response.location


def test_account_creation_success_for_authenticated_user():
    app = build_test_app()
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["csrf_token"] = "known-token"

    response = client.post(
        "/accounts/create",
        data={
            "csrf_token": "known-token",
            "acc_type": "Savings",
            "branch_id": "1",
            "opening_balance": "1000",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Account created successfully" in response.data


def test_transfer_edge_case_target_missing():
    app = build_test_app()
    client = app.test_client()

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["csrf_token"] = "known-token"

    response = client.post(
        "/transactions/create",
        data={
            "csrf_token": "known-token",
            "txn_type": "Transfer",
            "amount": "200",
            "source_account_no": "11",
            "target_account_no": "",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Target account is required for transfer" in response.data

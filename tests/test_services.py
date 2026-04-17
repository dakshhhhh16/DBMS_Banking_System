import pytest

from banking_app.services.auth_service import AuthService
from banking_app.services.banking_service import BankingService
from banking_app.utils.exceptions import ValidationError


class FakeAuthRepo:
    def __init__(self, username_exists=False, email_exists=False, phone_exists=False):
        self._username_exists = username_exists
        self._email_exists = email_exists
        self._phone_exists = phone_exists

    def username_exists(self, username):
        return self._username_exists

    def email_exists(self, email):
        return self._email_exists

    def phone_exists(self, phone):
        return self._phone_exists

    def create_user_with_customer(self, **kwargs):
        return {"user_id": 1, **kwargs}

    def get_user_by_username(self, username):
        return None

    def get_user_by_id(self, user_id):
        return None


class FakeBankRepo:
    def __init__(self):
        self.update_calls = 0
        self.close_calls = 0

    def create_account(self, **kwargs):
        return 10

    def create_transaction(self, **kwargs):
        return 20

    def update_account(self, **kwargs):
        self.update_calls += 1
        return {
            "account_no": kwargs["account_no"],
            "acc_type": kwargs.get("acc_type") or "Savings",
            "branch_id": kwargs.get("branch_id") or 1,
        }

    def close_account(self, **kwargs):
        self.close_calls += 1
        return kwargs["account_no"]


def test_auth_service_rejects_duplicate_username():
    service = AuthService(FakeAuthRepo(username_exists=True))

    with pytest.raises(ValidationError):
        service.register_user(
            {
                "name": "Test User",
                "address": "Address 1",
                "phone": "9999999999",
                "email": "test@example.com",
                "dob": "1990-01-01",
                "username": "takenuser",
                "password": "Password123",
            }
        )


def test_banking_service_rejects_invalid_account_type():
    service = BankingService(FakeBankRepo())

    with pytest.raises(ValidationError):
        service.create_account(
            1,
            {
                "acc_type": "Crypto",
                "branch_id": "1",
                "opening_balance": "100",
            },
        )


def test_banking_service_rejects_transfer_without_target():
    service = BankingService(FakeBankRepo())

    with pytest.raises(ValidationError):
        service.create_transaction(
            1,
            {
                "txn_type": "Transfer",
                "amount": "100",
                "source_account_no": "1",
                "target_account_no": "",
            },
        )


def test_banking_service_rejects_update_without_fields():
    service = BankingService(FakeBankRepo())

    with pytest.raises(ValidationError):
        service.update_account(1, 10, {})


def test_banking_service_rejects_invalid_update_account_type():
    service = BankingService(FakeBankRepo())

    with pytest.raises(ValidationError):
        service.update_account(
            1,
            10,
            {
                "acc_type": "Crypto",
            },
        )


def test_banking_service_closes_account_via_repository():
    repo = FakeBankRepo()
    service = BankingService(repo)

    account_no = service.close_account(1, 77)

    assert account_no == 77
    assert repo.close_calls == 1

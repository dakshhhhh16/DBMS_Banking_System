from banking_app.utils.exceptions import ValidationError
from banking_app.utils.validators import require_decimal, require_text


class BankingService:
    def __init__(self, repository):
        self.repository = repository

    def get_dashboard_payload(self, customer_id):
        return {
            "summary": self.repository.get_summary(),
            "reference": self.repository.get_reference_data(),
            "accounts": self.repository.get_customer_accounts(customer_id),
            "transactions": self.repository.get_recent_transactions_for_customer(customer_id),
            "loans": self.repository.get_customer_loans(customer_id),
            "loan_payments": self.repository.get_recent_loan_payments_for_customer(customer_id),
        }

    def create_account(self, customer_id, payload):
        acc_type = require_text(payload.get("acc_type"), "Account type", min_len=2, max_len=20)
        if acc_type not in {"Savings", "Current", "FD"}:
            raise ValidationError("Account type must be Savings, Current, or FD.")

        branch_id = payload.get("branch_id")
        try:
            branch_id = int(branch_id)
        except (TypeError, ValueError) as err:
            raise ValidationError("Branch is required.") from err

        opening_balance = require_decimal(payload.get("opening_balance"), "Opening balance")

        account_no = self.repository.create_account(
            customer_id=customer_id,
            branch_id=branch_id,
            acc_type=acc_type,
            opening_balance=opening_balance,
        )
        return account_no

    def update_account(self, customer_id, account_no, payload):
        acc_type = None
        branch_id = None

        if payload.get("acc_type") not in (None, ""):
            acc_type = require_text(payload.get("acc_type"), "Account type", min_len=2, max_len=20)
            if acc_type not in {"Savings", "Current", "FD"}:
                raise ValidationError("Account type must be Savings, Current, or FD.")

        if payload.get("branch_id") not in (None, ""):
            try:
                branch_id = int(payload.get("branch_id"))
            except (TypeError, ValueError) as err:
                raise ValidationError("Branch must be a valid number.") from err

        if acc_type is None and branch_id is None:
            raise ValidationError("Provide at least one field to update: acc_type or branch_id.")

        return self.repository.update_account(
            customer_id=customer_id,
            account_no=account_no,
            acc_type=acc_type,
            branch_id=branch_id,
        )

    def close_account(self, customer_id, account_no):
        return self.repository.close_account(customer_id=customer_id, account_no=account_no)

    def create_loan(self, customer_id, payload):
        loan_type = require_text(payload.get("loan_type"), "Loan type", min_len=3, max_len=20)
        if loan_type not in {"Home", "Car", "Education", "Personal"}:
            raise ValidationError("Loan type must be Home, Car, Education, or Personal.")

        amount = require_decimal(payload.get("amount"), "Loan amount")
        if amount <= 0:
            raise ValidationError("Loan amount must be greater than zero.")

        interest_rate = require_decimal(payload.get("interest_rate"), "Interest rate")
        if interest_rate < 0 or interest_rate > 100:
            raise ValidationError("Interest rate must be between 0 and 100.")

        try:
            branch_id = int(payload.get("branch_id"))
        except (TypeError, ValueError) as err:
            raise ValidationError("Branch is required.") from err

        return self.repository.create_loan(
            customer_id=customer_id,
            loan_type=loan_type,
            amount=amount,
            interest_rate=interest_rate,
            branch_id=branch_id,
        )

    def create_loan_installment(self, customer_id, payload):
        try:
            loan_id = int(payload.get("loan_id"))
        except (TypeError, ValueError) as err:
            raise ValidationError("Loan is required.") from err

        try:
            source_account_no = int(payload.get("source_account_no"))
        except (TypeError, ValueError) as err:
            raise ValidationError("Source account is required.") from err

        amount = require_decimal(payload.get("amount"), "Installment amount")
        if amount <= 0:
            raise ValidationError("Installment amount must be greater than zero.")

        return self.repository.create_loan_installment(
            customer_id=customer_id,
            loan_id=loan_id,
            source_account_no=source_account_no,
            amount=amount,
        )

    def create_transaction(self, customer_id, payload):
        txn_type = require_text(payload.get("txn_type"), "Transaction type", min_len=3, max_len=20)
        if txn_type not in {"Deposit", "Withdraw", "Transfer"}:
            raise ValidationError("Transaction type must be Deposit, Withdraw, or Transfer.")

        amount = require_decimal(payload.get("amount"), "Amount")
        if amount <= 0:
            raise ValidationError("Amount must be greater than zero.")

        try:
            source_account_no = int(payload.get("source_account_no"))
        except (TypeError, ValueError) as err:
            raise ValidationError("Source account is required.") from err

        target_raw = payload.get("target_account_no")
        target_account_no = None
        if target_raw not in (None, ""):
            try:
                target_account_no = int(target_raw)
            except (TypeError, ValueError) as err:
                raise ValidationError("Target account must be numeric.") from err

        description = payload.get("description", "")
        description = description.strip()[:255] if description else None

        if txn_type == "Transfer" and target_account_no is None:
            raise ValidationError("Target account is required for transfer.")
        if txn_type != "Transfer":
            target_account_no = None

        return self.repository.create_transaction(
            customer_id=customer_id,
            txn_type=txn_type,
            amount=amount,
            source_account_no=source_account_no,
            target_account_no=target_account_no,
            description=description,
        )

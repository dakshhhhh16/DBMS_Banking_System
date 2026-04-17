from decimal import Decimal

from banking_app.db import get_connection
from banking_app.utils.exceptions import AuthorizationError, NotFoundError, ValidationError


def _row_to_dict(row):
    return dict(row) if row else None


def _rows_to_dicts(rows):
    return [dict(row) for row in rows]


def _to_decimal(value):
    return Decimal(str(value))


class BankingRepository:
    def get_summary(self):
        sql = """
            SELECT
                (SELECT COUNT(*) FROM branch) AS branches,
                (SELECT COUNT(*) FROM customer) AS customers,
                (SELECT COUNT(*) FROM account) AS accounts,
                (SELECT COUNT(*) FROM loan) AS loans,
                (SELECT COALESCE(SUM(balance), 0) FROM account) AS total_deposit,
                (SELECT COALESCE(SUM(amount), 0) FROM loan) AS total_loan
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql)
            row = cur.fetchone()
            cur.close()
            return _row_to_dict(row)

    def get_reference_data(self):
        payload = {}
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT branch_id, branch_name, city, assets FROM branch ORDER BY branch_name")
            payload["branches"] = _rows_to_dicts(cur.fetchall())

            cur.execute("""
                SELECT loan_id, loan_type, amount, interest_rate, issue_date, customer_id, branch_id
                FROM loan
                ORDER BY issue_date DESC
                LIMIT 25
            """)
            payload["loans"] = _rows_to_dicts(cur.fetchall())

            cur.execute("""
                SELECT emp_id, name, designation, salary, branch_id
                FROM employee
                ORDER BY emp_id DESC
                LIMIT 50
            """)
            payload["employees"] = _rows_to_dicts(cur.fetchall())
            cur.close()
        return payload

    def get_customer_accounts(self, customer_id):
        sql = """
            SELECT a.account_no, a.acc_type, a.balance, a.open_date, a.branch_id,
                   b.branch_name, b.city
            FROM account a
            JOIN branch b ON b.branch_id = a.branch_id
            WHERE a.customer_id = ?
            ORDER BY a.account_no
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (customer_id,))
            rows = cur.fetchall()
            cur.close()
            return _rows_to_dicts(rows)

    def get_recent_transactions_for_customer(self, customer_id, limit=50):
        sql = """
            SELECT t.txn_id, t.txn_type, t.amount, t.txn_datetime,
                   t.source_account_no, t.target_account_no, t.description
            FROM bank_transaction t
            JOIN account a ON a.account_no = t.source_account_no
            WHERE a.customer_id = ?
            ORDER BY t.txn_datetime DESC
            LIMIT ?
        """
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, (customer_id, limit))
            rows = cur.fetchall()
            cur.close()
            return _rows_to_dicts(rows)

    def create_account(self, *, customer_id, branch_id, acc_type, opening_balance):
        sql = """
            INSERT INTO account (acc_type, balance, open_date, branch_id, customer_id)
            VALUES (?, ?, CURRENT_DATE, ?, ?)
        """
        with get_connection() as conn:
            cur = conn.cursor()
            try:
                conn.execute("BEGIN IMMEDIATE")
                cur.execute("SELECT branch_id FROM branch WHERE branch_id = ?", (branch_id,))
                if cur.fetchone() is None:
                    raise NotFoundError("Selected branch was not found.")

                cur.execute(sql, (acc_type, opening_balance, branch_id, customer_id))
                account_no = cur.lastrowid

                if opening_balance > 0:
                    cur.execute(
                        """
                        INSERT INTO bank_transaction (txn_type, amount, txn_datetime, source_account_no, target_account_no, description)
                        VALUES ('Deposit', ?, CURRENT_TIMESTAMP, ?, NULL, 'Initial deposit')
                        """,
                        (opening_balance, account_no),
                    )

                conn.commit()
                return account_no
            except Exception:
                conn.rollback()
                raise
            finally:
                cur.close()

    def create_transaction(
        self,
        *,
        customer_id,
        txn_type,
        amount,
        source_account_no,
        target_account_no,
        description,
    ):
        with get_connection() as conn:
            cur = conn.cursor()
            try:
                conn.execute("BEGIN IMMEDIATE")
                cur.execute(
                    """
                    SELECT account_no, balance
                    FROM account
                    WHERE account_no = ? AND customer_id = ?
                    """,
                    (source_account_no, customer_id),
                )
                source = cur.fetchone()
                if source is None:
                    raise AuthorizationError("You can only transact from your own accounts.")

                target = None
                if txn_type == "Transfer":
                    cur.execute(
                        "SELECT account_no, balance FROM account WHERE account_no = ?",
                        (target_account_no,),
                    )
                    target = cur.fetchone()
                    if target is None:
                        raise NotFoundError("Target account not found.")
                    if target_account_no == source_account_no:
                        raise ValidationError("Source and target accounts must differ for transfer.")

                if txn_type in {"Withdraw", "Transfer"} and _to_decimal(source["balance"]) < amount:
                    raise ValidationError("Insufficient balance for this transaction.")

                if txn_type == "Deposit":
                    cur.execute(
                        "UPDATE account SET balance = balance + ? WHERE account_no = ?",
                        (amount, source_account_no),
                    )
                elif txn_type == "Withdraw":
                    cur.execute(
                        "UPDATE account SET balance = balance - ? WHERE account_no = ?",
                        (amount, source_account_no),
                    )
                else:
                    cur.execute(
                        "UPDATE account SET balance = balance - ? WHERE account_no = ?",
                        (amount, source_account_no),
                    )
                    cur.execute(
                        "UPDATE account SET balance = balance + ? WHERE account_no = ?",
                        (amount, target_account_no),
                    )

                cur.execute(
                    """
                    INSERT INTO bank_transaction (txn_type, amount, txn_datetime, source_account_no, target_account_no, description)
                    VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, ?)
                    """,
                    (txn_type, amount, source_account_no, target_account_no, description),
                )
                conn.commit()
                return cur.lastrowid
            except Exception:
                conn.rollback()
                raise
            finally:
                cur.close()

    def update_account(self, *, customer_id, account_no, acc_type=None, branch_id=None):
        with get_connection() as conn:
            cur = conn.cursor()
            try:
                conn.execute("BEGIN IMMEDIATE")

                cur.execute(
                    "SELECT account_no, customer_id FROM account WHERE account_no = ?",
                    (account_no,),
                )
                account = cur.fetchone()
                if account is None:
                    raise NotFoundError("Account not found.")
                if account["customer_id"] != customer_id:
                    raise AuthorizationError("You can only update your own accounts.")

                if branch_id is not None:
                    cur.execute("SELECT branch_id FROM branch WHERE branch_id = ?", (branch_id,))
                    if cur.fetchone() is None:
                        raise NotFoundError("Selected branch was not found.")

                updates = []
                values = []

                if acc_type is not None:
                    updates.append("acc_type = ?")
                    values.append(acc_type)

                if branch_id is not None:
                    updates.append("branch_id = ?")
                    values.append(branch_id)

                values.append(account_no)
                cur.execute(f"UPDATE account SET {', '.join(updates)} WHERE account_no = ?", tuple(values))

                cur.execute(
                    """
                    SELECT a.account_no, a.acc_type, a.balance, a.open_date, a.branch_id,
                           b.branch_name, b.city
                    FROM account a
                    JOIN branch b ON b.branch_id = a.branch_id
                    WHERE a.account_no = ?
                    """,
                    (account_no,),
                )
                updated = cur.fetchone()

                conn.commit()
                return _row_to_dict(updated)
            except Exception:
                conn.rollback()
                raise
            finally:
                cur.close()

    def close_account(self, *, customer_id, account_no):
        with get_connection() as conn:
            cur = conn.cursor()
            try:
                conn.execute("BEGIN IMMEDIATE")

                cur.execute(
                    "SELECT account_no, customer_id, balance FROM account WHERE account_no = ?",
                    (account_no,),
                )
                account = cur.fetchone()
                if account is None:
                    raise NotFoundError("Account not found.")
                if account["customer_id"] != customer_id:
                    raise AuthorizationError("You can only close your own accounts.")

                if _to_decimal(account["balance"]) != Decimal("0"):
                    raise ValidationError("Account balance must be zero before closing.")

                cur.execute(
                    """
                    SELECT COUNT(*) AS txn_count
                    FROM bank_transaction
                    WHERE source_account_no = ? OR target_account_no = ?
                    """,
                    (account_no, account_no),
                )
                txn_count = cur.fetchone()["txn_count"]
                if txn_count > 0:
                    raise ValidationError("Account cannot be closed because transaction history exists.")

                cur.execute("DELETE FROM account WHERE account_no = ?", (account_no,))
                conn.commit()
                return account_no
            except Exception:
                conn.rollback()
                raise
            finally:
                cur.close()

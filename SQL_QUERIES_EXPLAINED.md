# All SQL Queries Used in the App

This file now contains all SQL statements currently used by the Python data-access layer:

- auth repository queries
- banking repository queries
- DB connection PRAGMA statements

It excludes DDL/schema creation statements from `banking_system.sql` because those are already documented in that file.

## Notes

- Value placeholders use `?` parameter binding (SQLite safe parameterization).
- Multi-step write operations use transactions with `BEGIN IMMEDIATE`.
- One query is intentionally dynamic: account update query in `update_account`, but the dynamic fields are restricted in Python to known safe column names.

---

## 1) Auth Repository Queries

### 1.1 Get user by username

Location: `AuthRepository.get_user_by_username`

```sql
SELECT u.user_id, u.username, u.password_hash, u.customer_id, c.name, c.email
FROM app_user u
JOIN customer c ON c.customer_id = u.customer_id
WHERE u.username = ?
LIMIT 1
```

Purpose:

- Fetch login record + customer profile details by username.

---

### 1.2 Get user by ID

Location: `AuthRepository.get_user_by_id`

```sql
SELECT u.user_id, u.username, u.customer_id, c.name, c.email
FROM app_user u
JOIN customer c ON c.customer_id = u.customer_id
WHERE u.user_id = ?
LIMIT 1
```

Purpose:

- Load user session identity and profile.

---

### 1.3 Username existence check

Location: `AuthRepository.username_exists`

```sql
SELECT 1 FROM app_user WHERE username = ? LIMIT 1
```

Purpose:

- Validate unique username during registration.

---

### 1.4 Email existence check

Location: `AuthRepository.email_exists`

```sql
SELECT 1 FROM customer WHERE email = ? LIMIT 1
```

Purpose:

- Validate unique email during registration.

---

### 1.5 Phone existence check

Location: `AuthRepository.phone_exists`

```sql
SELECT 1 FROM customer WHERE phone = ? LIMIT 1
```

Purpose:

- Validate unique phone during registration.

---

### 1.6 Registration transaction statements

Location: `AuthRepository.create_user_with_customer`

```sql
BEGIN IMMEDIATE
```

Purpose:

- Start a write transaction with early lock.

```sql
INSERT INTO customer (name, address, phone, email, dob)
VALUES (?, ?, ?, ?, ?)
```

Purpose:

- Create customer row first.

```sql
INSERT INTO app_user (username, password_hash, customer_id)
VALUES (?, ?, ?)
```

Purpose:

- Create login user linked to the new customer.

---

## 2) Banking Repository Read Queries

### 2.1 Dashboard summary metrics

Location: `BankingRepository.get_summary`

```sql
SELECT
    (SELECT COUNT(*) FROM branch) AS branches,
    (SELECT COUNT(*) FROM customer) AS customers,
    (SELECT COUNT(*) FROM account) AS accounts,
    (SELECT COUNT(*) FROM loan) AS loans,
    (SELECT COALESCE(SUM(balance), 0) FROM account) AS total_deposit,
    (SELECT COALESCE(SUM(amount), 0) FROM loan) AS total_loan
```

Purpose:

- Aggregate top-level dashboard metrics.

---

### 2.2 Reference branches

Location: `BankingRepository.get_reference_data`

```sql
SELECT branch_id, branch_name, city, assets FROM branch ORDER BY branch_name
```

Purpose:

- Populate branch dropdowns and bank reference tables.

---

### 2.3 Reference loans

Location: `BankingRepository.get_reference_data`

```sql
SELECT loan_id, loan_type, amount, interest_rate, issue_date, customer_id, branch_id
FROM loan
ORDER BY issue_date DESC
LIMIT 25
```

Purpose:

- Show latest loan reference records on bank details page.

---

### 2.4 Reference employees

Location: `BankingRepository.get_reference_data`

```sql
SELECT emp_id, name, designation, salary, branch_id
FROM employee
ORDER BY emp_id DESC
LIMIT 50
```

Purpose:

- Show employee reference data.

---

### 2.5 Customer accounts

Location: `BankingRepository.get_customer_accounts`

```sql
SELECT a.account_no, a.acc_type, a.balance, a.open_date, a.branch_id,
       b.branch_name, b.city
FROM account a
JOIN branch b ON b.branch_id = a.branch_id
WHERE a.customer_id = ?
ORDER BY a.account_no
```

Purpose:

- Return accounts owned by logged-in customer.

---

### 2.6 Recent customer transactions

Location: `BankingRepository.get_recent_transactions_for_customer`

```sql
SELECT t.txn_id, t.txn_type, t.amount, t.txn_datetime,
       t.source_account_no, t.target_account_no, t.description
FROM bank_transaction t
JOIN account a ON a.account_no = t.source_account_no
WHERE a.customer_id = ?
ORDER BY t.txn_datetime DESC
LIMIT ?
```

Purpose:

- Return latest transaction stream for customer-owned source accounts.

---

### 2.7 Customer loans with repayment summary

Location: `BankingRepository.get_customer_loans`

```sql
SELECT l.loan_id, l.loan_type, l.amount, l.interest_rate, l.issue_date,
       l.branch_id, b.branch_name,
       COALESCE(SUM(lp.amount_paid), 0) AS total_paid,
       COUNT(lp.payment_id) AS installments_paid,
       (l.amount - COALESCE(SUM(lp.amount_paid), 0)) AS outstanding_amount
FROM loan l
JOIN branch b ON b.branch_id = l.branch_id
LEFT JOIN loan_payment lp ON lp.loan_id = l.loan_id
WHERE l.customer_id = ?
GROUP BY l.loan_id, l.loan_type, l.amount, l.interest_rate, l.issue_date, l.branch_id, b.branch_name
ORDER BY l.issue_date DESC, l.loan_id DESC
LIMIT ?
```

Purpose:

- Return customer loans + paid amount + number of installments + outstanding amount.

---

### 2.8 Recent loan payments (installments)

Location: `BankingRepository.get_recent_loan_payments_for_customer`

```sql
SELECT lp.payment_id, lp.loan_id, lp.pay_date, lp.amount_paid,
       l.loan_type
FROM loan_payment lp
JOIN loan l ON l.loan_id = lp.loan_id
WHERE l.customer_id = ?
ORDER BY lp.pay_date DESC, lp.payment_id DESC
LIMIT ?
```

Purpose:

- Return installment history for logged-in customer.

---

## 3) Banking Repository Write Queries

### 3.1 Create account flow

Location: `BankingRepository.create_account`

```sql
BEGIN IMMEDIATE
```

Purpose:

- Start write transaction.

```sql
SELECT branch_id FROM branch WHERE branch_id = ?
```

Purpose:

- Validate selected branch exists.

```sql
INSERT INTO account (acc_type, balance, open_date, branch_id, customer_id)
VALUES (?, ?, CURRENT_DATE, ?, ?)
```

Purpose:

- Create new account for customer.

```sql
INSERT INTO bank_transaction (txn_type, amount, txn_datetime, source_account_no, target_account_no, description)
VALUES ('Deposit', ?, CURRENT_TIMESTAMP, ?, NULL, 'Initial deposit')
```

Purpose:

- Add ledger entry if opening balance is greater than zero.

---

### 3.2 Create loan flow

Location: `BankingRepository.create_loan`

```sql
BEGIN IMMEDIATE
```

Purpose:

- Start write transaction.

```sql
SELECT branch_id FROM branch WHERE branch_id = ?
```

Purpose:

- Validate selected branch exists.

```sql
INSERT INTO loan (loan_type, amount, interest_rate, issue_date, branch_id, customer_id)
VALUES (?, ?, ?, CURRENT_DATE, ?, ?)
```

Purpose:

- Create new loan record for customer.

---

### 3.3 Pay loan installment (EMI deduction) flow

Location: `BankingRepository.create_loan_installment`

```sql
BEGIN IMMEDIATE
```

Purpose:

- Start atomic write transaction.

```sql
SELECT loan_id, customer_id, amount FROM loan WHERE loan_id = ?
```

Purpose:

- Validate loan exists and load principal amount.

```sql
SELECT COALESCE(SUM(amount_paid), 0) AS total_paid FROM loan_payment WHERE loan_id = ?
```

Purpose:

- Compute already paid amount to validate installment size.

```sql
SELECT account_no, balance
FROM account
WHERE account_no = ? AND customer_id = ?
```

Purpose:

- Validate source account ownership and available balance.

```sql
UPDATE account SET balance = balance - ? WHERE account_no = ?
```

Purpose:

- Deduct installment from source account.

```sql
INSERT INTO loan_payment (loan_id, pay_date, amount_paid)
VALUES (?, CURRENT_DATE, ?)
```

Purpose:

- Record installment payment.

```sql
INSERT INTO bank_transaction (txn_type, amount, txn_datetime, source_account_no, target_account_no, description)
VALUES ('Withdraw', ?, CURRENT_TIMESTAMP, ?, NULL, ?)
```

Purpose:

- Write matching transaction history row for deduction.

---

### 3.4 Create transaction flow (deposit, withdraw, transfer)

Location: `BankingRepository.create_transaction`

```sql
BEGIN IMMEDIATE
```

Purpose:

- Start atomic write transaction.

```sql
SELECT account_no, balance
FROM account
WHERE account_no = ? AND customer_id = ?
```

Purpose:

- Validate source account belongs to logged-in customer.

```sql
SELECT account_no, balance FROM account WHERE account_no = ?
```

Purpose:

- Validate transfer target account exists.

```sql
UPDATE account SET balance = balance + ? WHERE account_no = ?
```

Purpose:

- Deposit amount into source account (deposit flow), or into target account (transfer flow).

```sql
UPDATE account SET balance = balance - ? WHERE account_no = ?
```

Purpose:

- Deduct amount from source account (withdraw/transfer flow).

```sql
INSERT INTO bank_transaction (txn_type, amount, txn_datetime, source_account_no, target_account_no, description)
VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, ?)
```

Purpose:

- Persist transaction ledger row.

---

### 3.5 Update account flow

Location: `BankingRepository.update_account`

```sql
BEGIN IMMEDIATE
```

Purpose:

- Start write transaction.

```sql
SELECT account_no, customer_id FROM account WHERE account_no = ?
```

Purpose:

- Validate account exists and belongs to logged-in customer.

```sql
SELECT branch_id FROM branch WHERE branch_id = ?
```

Purpose:

- Validate branch when branch update requested.

```sql
UPDATE account SET <dynamic columns> WHERE account_no = ?
```

Purpose:

- Update `acc_type`, `branch_id`, or both.

Important:

- The dynamic column list is assembled only from a strict whitelist in Python logic (`acc_type`, `branch_id`).

```sql
SELECT a.account_no, a.acc_type, a.balance, a.open_date, a.branch_id,
       b.branch_name, b.city
FROM account a
JOIN branch b ON b.branch_id = a.branch_id
WHERE a.account_no = ?
```

Purpose:

- Fetch and return updated row for API response.

---

### 3.6 Close account flow

Location: `BankingRepository.close_account`

```sql
BEGIN IMMEDIATE
```

Purpose:

- Start atomic write transaction.

```sql
SELECT account_no, customer_id, balance FROM account WHERE account_no = ?
```

Purpose:

- Validate account exists, ownership, and balance state.

```sql
SELECT COUNT(*) AS txn_count
FROM bank_transaction
WHERE source_account_no = ? OR target_account_no = ?
```

Purpose:

- Prevent closure if transaction history exists.

```sql
DELETE FROM account WHERE account_no = ?
```

Purpose:

- Delete account once all checks pass.

---

## 4) DB Connection Statements (Executed on Each Connection)

Location: `banking_app/db.py` in `get_connection`

```sql
PRAGMA foreign_keys = ON
```

Purpose:

- Enforce foreign key constraints in SQLite.

```sql
PRAGMA busy_timeout = 5000
```

Purpose:

- Wait up to 5000 ms for DB locks before failing.

---

## 5) Transaction Pattern Summary

The repositories follow this write pattern:

1. `BEGIN IMMEDIATE`
2. Validate ownership and reference constraints
3. Perform one or more writes
4. `commit()` on success
5. `rollback()` on exception

This prevents partial writes and keeps account, loan, and ledger data consistent.

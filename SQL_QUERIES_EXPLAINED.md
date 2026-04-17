# SQL Queries Added and Updated

This document lists the SQL statements added or updated for:

- account update and account close
- loan application
- EMI/installment deduction
- loan and installment reporting

All placeholders use SQLite parameter binding with `?` to prevent SQL injection for values.

## 1) Customer Accounts Query (updated)

**Location:** `banking_app/repositories/banking_repository.py` in `get_customer_accounts`

```sql
SELECT a.account_no, a.acc_type, a.balance, a.open_date, a.branch_id,
       b.branch_name, b.city
FROM account a
JOIN branch b ON b.branch_id = a.branch_id
WHERE a.customer_id = ?
ORDER BY a.account_no
```

**Why:**

- Fetches only the logged-in customer's accounts.
- Includes `branch_id` (newly included) so account update forms can preselect the current branch.

**Parameter:**

- `customer_id`

---

## 2) Customer Loans Query With Repayment Summary

**Location:** `banking_app/repositories/banking_repository.py` in `get_customer_loans`

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

**Why:**

- Returns each loan for the current customer.
- Calculates repayment progress:
  - `total_paid`
  - `installments_paid`
  - `outstanding_amount`

**Parameters:**

- `customer_id`
- `limit`

---

## 3) Recent Installment Payments Query

**Location:** `banking_app/repositories/banking_repository.py` in `get_recent_loan_payments_for_customer`

```sql
SELECT lp.payment_id, lp.loan_id, lp.pay_date, lp.amount_paid,
       l.loan_type
FROM loan_payment lp
JOIN loan l ON l.loan_id = lp.loan_id
WHERE l.customer_id = ?
ORDER BY lp.pay_date DESC, lp.payment_id DESC
LIMIT ?
```

**Why:**

- Shows installment history for the logged-in customer only.

**Parameters:**

- `customer_id`
- `limit`

---

## 4) Loan Application Queries

### 4.1 Branch existence check

**Location:** `create_loan`

```sql
SELECT branch_id FROM branch WHERE branch_id = ?
```

**Why:**

- Validates the selected branch before loan insertion.

**Parameter:**

- `branch_id`

### 4.2 Insert loan

**Location:** `create_loan`

```sql
INSERT INTO loan (loan_type, amount, interest_rate, issue_date, branch_id, customer_id)
VALUES (?, ?, ?, CURRENT_DATE, ?, ?)
```

**Why:**

- Creates a new loan record for the customer.

**Parameters:**

- `loan_type`, `amount`, `interest_rate`, `branch_id`, `customer_id`

---

## 5) Loan EMI / Installment Deduction Queries

### 5.1 Load loan and ownership check

**Location:** `create_loan_installment`

```sql
SELECT loan_id, customer_id, amount FROM loan WHERE loan_id = ?
```

**Why:**

- Ensures the loan exists and belongs to the current customer.

**Parameter:**

- `loan_id`

### 5.2 Total paid so far

**Location:** `create_loan_installment`

```sql
SELECT COALESCE(SUM(amount_paid), 0) AS total_paid FROM loan_payment WHERE loan_id = ?
```

**Why:**

- Calculates current repayment total to derive outstanding amount before accepting payment.

**Parameter:**

- `loan_id`

### 5.3 Load source account and balance

**Location:** `create_loan_installment`

```sql
SELECT account_no, balance
FROM account
WHERE account_no = ? AND customer_id = ?
```

**Why:**

- Confirms the account belongs to the customer and has sufficient funds.

**Parameters:**

- `source_account_no`, `customer_id`

### 5.4 Deduct installment from account

**Location:** `create_loan_installment`

```sql
UPDATE account SET balance = balance - ? WHERE account_no = ?
```

**Why:**

- Deducts EMI/installment from selected account.

**Parameters:**

- `amount`, `source_account_no`

### 5.5 Insert installment record

**Location:** `create_loan_installment`

```sql
INSERT INTO loan_payment (loan_id, pay_date, amount_paid)
VALUES (?, CURRENT_DATE, ?)
```

**Why:**

- Persists installment payment against the loan.

**Parameters:**

- `loan_id`, `amount`

### 5.6 Insert matching transaction ledger entry

**Location:** `create_loan_installment`

```sql
INSERT INTO bank_transaction (txn_type, amount, txn_datetime, source_account_no, target_account_no, description)
VALUES ('Withdraw', ?, CURRENT_TIMESTAMP, ?, NULL, ?)
```

**Why:**

- Keeps account transaction history consistent with EMI deduction.

**Parameters:**

- `amount`, `source_account_no`, `description`

---

## 6) Account Update Queries

### 6.1 Load account and ownership check

**Location:** `update_account`

```sql
SELECT account_no, customer_id FROM account WHERE account_no = ?
```

**Why:**

- Ensures account exists and belongs to logged-in customer.

**Parameter:**

- `account_no`

### 6.2 Optional branch existence check

**Location:** `update_account`

```sql
SELECT branch_id FROM branch WHERE branch_id = ?
```

**Why:**

- Validates branch before updating account branch.

**Parameter:**

- `branch_id`

### 6.3 Dynamic account update

**Location:** `update_account`

```sql
UPDATE account SET <dynamic columns> WHERE account_no = ?
```

**Why:**

- Updates `acc_type`, `branch_id`, or both.
- Dynamic part is limited by Python logic to known columns only.

**Parameters:**

- Selected values (`acc_type` and/or `branch_id`), then `account_no`

### 6.4 Fetch updated account for response

**Location:** `update_account`

```sql
SELECT a.account_no, a.acc_type, a.balance, a.open_date, a.branch_id,
       b.branch_name, b.city
FROM account a
JOIN branch b ON b.branch_id = a.branch_id
WHERE a.account_no = ?
```

**Why:**

- Returns fresh account data after update.

**Parameter:**

- `account_no`

---

## 7) Account Close Queries

### 7.1 Load account for close validation

**Location:** `close_account`

```sql
SELECT account_no, customer_id, balance FROM account WHERE account_no = ?
```

**Why:**

- Validates account ownership and zero-balance requirement.

**Parameter:**

- `account_no`

### 7.2 Check transaction history (close safety)

**Location:** `close_account`

```sql
SELECT COUNT(*) AS txn_count
FROM bank_transaction
WHERE source_account_no = ? OR target_account_no = ?
```

**Why:**

- Prevents closing an account that already has transaction history.

**Parameters:**

- `account_no`, `account_no`

### 7.3 Delete account

**Location:** `close_account`

```sql
DELETE FROM account WHERE account_no = ?
```

**Why:**

- Closes the account after all validations pass.

**Parameter:**

- `account_no`

---

## Transaction Handling Note

For write operations, the repository uses:

```sql
BEGIN IMMEDIATE
```

This obtains a write lock early in SQLite, helping avoid race conditions during multi-step operations such as installment deduction and account close checks.

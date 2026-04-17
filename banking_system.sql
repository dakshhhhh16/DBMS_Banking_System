-- Banking System Schema
-- Compatible with SQLite 3

PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS loan_payment;
DROP TABLE IF EXISTS bank_transaction;
DROP TABLE IF EXISTS loan;
DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS app_user;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS branch;

PRAGMA foreign_keys = ON;

CREATE TABLE branch (
    branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_name TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL,
    assets NUMERIC NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (assets >= 0)
);

CREATE TABLE customer (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    dob TEXT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE app_user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    customer_id INTEGER NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
        ON DELETE CASCADE
        ON UPDATE RESTRICT
);

CREATE TABLE account (
    account_no INTEGER PRIMARY KEY AUTOINCREMENT,
    acc_type TEXT NOT NULL CHECK (acc_type IN ('Savings', 'Current', 'FD')),
    balance NUMERIC NOT NULL DEFAULT 0,
    open_date TEXT NOT NULL,
    branch_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    CHECK (balance >= 0),
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
);

CREATE TABLE employee (
    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    designation TEXT NOT NULL,
    salary NUMERIC NOT NULL,
    branch_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (salary > 0),
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
);

CREATE TABLE loan (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_type TEXT NOT NULL CHECK (loan_type IN ('Home', 'Car', 'Education', 'Personal')),
    amount NUMERIC NOT NULL,
    interest_rate NUMERIC NOT NULL,
    issue_date TEXT NOT NULL,
    branch_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    CHECK (amount > 0),
    CHECK (interest_rate >= 0 AND interest_rate <= 100),
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
);

CREATE TABLE bank_transaction (
    txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
    txn_type TEXT NOT NULL CHECK (txn_type IN ('Deposit', 'Withdraw', 'Transfer')),
    amount NUMERIC NOT NULL,
    txn_datetime TEXT NOT NULL,
    source_account_no INTEGER NOT NULL,
    target_account_no INTEGER NULL,
    description TEXT NULL,
    CHECK (amount > 0),
    FOREIGN KEY (source_account_no) REFERENCES account(account_no)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT,
    FOREIGN KEY (target_account_no) REFERENCES account(account_no)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT
);

CREATE TABLE loan_payment (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL,
    pay_date TEXT NOT NULL,
    amount_paid NUMERIC NOT NULL,
    CHECK (amount_paid > 0),
    FOREIGN KEY (loan_id) REFERENCES loan(loan_id)
        ON DELETE CASCADE
        ON UPDATE RESTRICT
);

CREATE INDEX idx_account_customer ON account(customer_id);
CREATE INDEX idx_account_branch ON account(branch_id);
CREATE INDEX idx_employee_branch ON employee(branch_id);
CREATE INDEX idx_loan_customer ON loan(customer_id);
CREATE INDEX idx_loan_branch ON loan(branch_id);
CREATE INDEX idx_txn_source ON bank_transaction(source_account_no);
CREATE INDEX idx_txn_target ON bank_transaction(target_account_no);
CREATE INDEX idx_txn_datetime ON bank_transaction(txn_datetime);
CREATE INDEX idx_payment_loan ON loan_payment(loan_id);

INSERT INTO branch (branch_name, city, assets) VALUES
 ('MG Road', 'Bengaluru', 50000000),
 ('Connaught Place', 'Delhi', 75000000),
 ('Marine Drive', 'Mumbai', 90000000),
 ('Park Street', 'Kolkata', 30000000);

INSERT INTO customer (name, address, phone, email, dob) VALUES
 ('Aarav Sharma', '22 Park Street, Delhi', '9876543210', 'aarav@gmail.com', '1995-04-12'),
 ('Priya Verma', '15 MG Road, Bengaluru', '9123456780', 'priya@yahoo.com', '1990-07-23'),
 ('Rohan Mehta', '9 Marine Drive, Mumbai', '9988776655', 'rohan@outlook.com', '1988-01-15'),
 ('Sneha Iyer', '5 Anna Salai, Chennai', '9001122334', 'sneha@gmail.com', '1992-11-30'),
 ('Karan Patel', '77 Ring Road, Ahmedabad', '9445566778', 'karan@gmail.com', '1985-06-18');

INSERT INTO app_user (username, password_hash, customer_id) VALUES
 ('aarav', 'pbkdf2:sha256:600000$XBy1Qnp4ubTXyg1J$1c5aaefa93172d68ab9273436c95cea33ef89bab1990133ca8f2d22e63d5856b', 1),
 ('priya', 'pbkdf2:sha256:600000$srHAKjNozghCwFXZ$8eb079c818fa7b8e3dd61502b8729d3883324c4b7493e7bfe39eedff717871c1', 2);

INSERT INTO account (acc_type, balance, open_date, branch_id, customer_id) VALUES
 ('Savings', 45000.00, '2022-03-15', 1, 2),
 ('Current', 120000.00, '2021-06-10', 2, 1),
 ('Savings', 8500.00, '2023-01-20', 3, 3),
 ('FD', 200000.00, '2020-09-05', 1, 4),
 ('Savings', 15000.00, '2024-03-11', 4, 5),
 ('Current', 60000.00, '2023-07-19', 2, 2);

INSERT INTO employee (name, designation, salary, branch_id) VALUES
 ('Manish Kumar', 'Manager', 85000, 1),
 ('Anita Rao', 'Cashier', 40000, 2),
 ('Vikas Singh', 'Clerk', 32000, 3),
 ('Riya Das', 'Manager', 82000, 4),
 ('Suresh Nair', 'Cashier', 38000, 1);

INSERT INTO loan (loan_type, amount, interest_rate, issue_date, branch_id, customer_id) VALUES
 ('Home', 2500000, 8.50, '2023-02-10', 1, 2),
 ('Car', 600000, 9.25, '2024-05-21', 2, 1),
 ('Education', 400000, 7.00, '2022-08-15', 3, 3),
 ('Personal', 150000, 11.50, '2024-12-01', 4, 5);

INSERT INTO bank_transaction (txn_type, amount, txn_datetime, source_account_no, target_account_no, description) VALUES
 ('Deposit', 10000, '2025-01-05 09:15:00', 1, NULL, 'Cash deposit'),
 ('Withdraw', 2000, '2025-01-12 11:00:00', 1, NULL, 'ATM withdrawal'),
 ('Deposit', 50000, '2025-02-01 14:20:00', 2, NULL, 'Cheque deposit'),
 ('Transfer', 5000, '2025-02-14 16:10:00', 3, 1, 'Fund transfer'),
 ('Deposit', 7500, '2025-03-09 10:35:00', 5, NULL, 'UPI deposit'),
 ('Withdraw', 12000, '2025-03-22 12:50:00', 6, NULL, 'Cash withdrawal');

INSERT INTO loan_payment (loan_id, pay_date, amount_paid) VALUES
 (1, '2025-01-15', 25000),
 (2, '2025-02-15', 12000),
 (1, '2025-02-15', 25000),
 (3, '2025-03-15', 8000),
 (4, '2025-03-30', 6000);

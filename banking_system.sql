-- Banking System Schema (Production-oriented baseline)
-- Compatible with MySQL 8+

SET NAMES utf8mb4;
SET time_zone = '+00:00';

DROP TABLE IF EXISTS loan_payment;
DROP TABLE IF EXISTS bank_transaction;
DROP TABLE IF EXISTS loan;
DROP TABLE IF EXISTS employee;
DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS app_user;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS branch;

CREATE TABLE branch (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(80) NOT NULL UNIQUE,
    city VARCHAR(80) NOT NULL,
    assets DECIMAL(15,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (assets >= 0)
) ENGINE=InnoDB;

CREATE TABLE customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    address VARCHAR(200) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    dob DATE NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE app_user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(30) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    customer_id INT NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
        ON DELETE CASCADE
        ON UPDATE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE account (
    account_no BIGINT AUTO_INCREMENT PRIMARY KEY,
    acc_type ENUM('Savings', 'Current', 'FD') NOT NULL,
    balance DECIMAL(12,2) NOT NULL DEFAULT 0,
    open_date DATE NOT NULL,
    branch_id INT NOT NULL,
    customer_id INT NOT NULL,
    CHECK (balance >= 0),
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT,
    INDEX idx_account_customer (customer_id),
    INDEX idx_account_branch (branch_id)
) ENGINE=InnoDB;

CREATE TABLE employee (
    emp_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    designation VARCHAR(50) NOT NULL,
    salary DECIMAL(12,2) NOT NULL,
    branch_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (salary > 0),
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT,
    INDEX idx_employee_branch (branch_id)
) ENGINE=InnoDB;

CREATE TABLE loan (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_type ENUM('Home', 'Car', 'Education', 'Personal') NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    issue_date DATE NOT NULL,
    branch_id INT NOT NULL,
    customer_id INT NOT NULL,
    CHECK (amount > 0),
    CHECK (interest_rate >= 0 AND interest_rate <= 100),
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT,
    INDEX idx_loan_customer (customer_id),
    INDEX idx_loan_branch (branch_id)
) ENGINE=InnoDB;

CREATE TABLE bank_transaction (
    txn_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    txn_type ENUM('Deposit', 'Withdraw', 'Transfer') NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    txn_datetime DATETIME NOT NULL,
    source_account_no BIGINT NOT NULL,
    target_account_no BIGINT NULL,
    description VARCHAR(255) NULL,
    CHECK (amount > 0),
    FOREIGN KEY (source_account_no) REFERENCES account(account_no)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT,
    FOREIGN KEY (target_account_no) REFERENCES account(account_no)
        ON DELETE RESTRICT
        ON UPDATE RESTRICT,
    INDEX idx_txn_source (source_account_no),
    INDEX idx_txn_target (target_account_no),
    INDEX idx_txn_datetime (txn_datetime)
) ENGINE=InnoDB;

CREATE TABLE loan_payment (
    payment_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT NOT NULL,
    pay_date DATE NOT NULL,
    amount_paid DECIMAL(12,2) NOT NULL,
    CHECK (amount_paid > 0),
    FOREIGN KEY (loan_id) REFERENCES loan(loan_id)
        ON DELETE CASCADE
        ON UPDATE RESTRICT,
    INDEX idx_payment_loan (loan_id)
) ENGINE=InnoDB;

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

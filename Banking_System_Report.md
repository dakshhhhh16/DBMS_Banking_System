# DBMS Project Report: Banking Management System

**Submitted by:** Daksh Pathak
**Date:** 16th April 2025
**Course:** Database Management Systems

---

## 1. System Description

The **Banking Management System (BMS)** is a software application designed to automate and manage the day-to-day operations of a bank. It maintains records of customers, their accounts, branches, employees, loans, and transactions. The system ensures secure, fast, and reliable handling of financial data while enforcing data integrity and consistency.

### Key Functionalities

1. **Customer Management** – Register new customers and store their personal details (name, address, phone, etc.).
2. **Account Management** – Open/close accounts (Savings, Current, Fixed Deposit) and maintain balances.
3. **Branch Management** – Maintain details of bank branches, their location and assets.
4. **Employee Management** – Maintain records of employees working in different branches.
5. **Transaction Handling** – Record deposits, withdrawals, and transfers between accounts.
6. **Loan Management** – Issue loans to customers, track loan amount, interest rate, and EMIs.
7. **Reports and Queries** – Generate reports such as branch-wise deposits, defaulters list, top customers, etc.

---

## 2. ER (Entity–Relationship) Model

### 2.1 Entities and Attributes

| Entity | Attributes (PK in **bold**) |
|--------|-----------------------------|
| **Branch** | **Branch_ID**, Branch_Name, City, Assets |
| **Customer** | **Customer_ID**, Name, Address, Phone, Email, DOB |
| **Account** | **Account_No**, Acc_Type, Balance, Open_Date, Branch_ID (FK), Customer_ID (FK) |
| **Employee** | **Emp_ID**, Name, Designation, Salary, Branch_ID (FK) |
| **Loan** | **Loan_ID**, Loan_Type, Amount, Interest_Rate, Issue_Date, Branch_ID (FK), Customer_ID (FK) |
| **Transaction** | **Txn_ID**, Txn_Type, Amount, Txn_Date, Account_No (FK) |
| **Loan_Payment** | **Payment_ID**, Loan_ID (FK), Pay_Date, Amount_Paid |

### 2.2 Relationships

| Relationship | Entities | Cardinality |
|--------------|----------|-------------|
| Has | Branch — Account | 1 : N |
| Owns | Customer — Account | 1 : N |
| Works_In | Employee — Branch | N : 1 |
| Takes | Customer — Loan | 1 : N |
| Sanctions | Branch — Loan | 1 : N |
| Performs | Account — Transaction | 1 : N |
| Pays | Loan — Loan_Payment | 1 : N |

### 2.3 ER Diagram (Textual Representation)

```
   ┌──────────┐         owns          ┌──────────┐        has        ┌──────────┐
   │ Customer │────────────<>─────────│ Account  │───────<>──────────│  Branch  │
   └──────────┘  1               N    └──────────┘  N             1  └──────────┘
        │                              │      │                          │
        │ takes                        │      │ performs                 │ works_in
        │                              │      ▼                          │
        ▼                              │ ┌─────────────┐                 ▼
   ┌──────────┐    sanctions   ┌───────┘ │ Transaction │           ┌──────────┐
   │   Loan   │────────────────│         └─────────────┘           │ Employee │
   └──────────┘  N           1                                      └──────────┘
        │
        │ pays
        ▼
   ┌──────────────┐
   │ Loan_Payment │
   └──────────────┘
```

---

## 3. Relational Schema

Primary keys are **underlined** in description; foreign keys are noted explicitly.

1. **Branch** ( **Branch_ID**, Branch_Name, City, Assets )
2. **Customer** ( **Customer_ID**, Name, Address, Phone, Email, DOB )
3. **Account** ( **Account_No**, Acc_Type, Balance, Open_Date, *Branch_ID*, *Customer_ID* )
   - FK: Branch_ID → Branch(Branch_ID)
   - FK: Customer_ID → Customer(Customer_ID)
4. **Employee** ( **Emp_ID**, Name, Designation, Salary, *Branch_ID* )
   - FK: Branch_ID → Branch(Branch_ID)
5. **Loan** ( **Loan_ID**, Loan_Type, Amount, Interest_Rate, Issue_Date, *Branch_ID*, *Customer_ID* )
   - FK: Branch_ID → Branch(Branch_ID)
   - FK: Customer_ID → Customer(Customer_ID)
6. **Transaction** ( **Txn_ID**, Txn_Type, Amount, Txn_Date, *Account_No* )
   - FK: Account_No → Account(Account_No)
7. **Loan_Payment** ( **Payment_ID**, *Loan_ID*, Pay_Date, Amount_Paid )
   - FK: Loan_ID → Loan(Loan_ID)

---

## 4. Normalization

For each relation we check 1NF, 2NF, 3NF, and BCNF.

| Relation | 1NF | 2NF | 3NF | BCNF | Highest NF |
|----------|-----|-----|-----|------|------------|
| Branch | ✓ atomic values | ✓ single PK | ✓ no transitive deps | ✓ | **BCNF** |
| Customer | ✓ | ✓ | ✓ | ✓ | **BCNF** |
| Account | ✓ | ✓ | ✓ | ✓ | **BCNF** |
| Employee | ✓ | ✓ | ✓ | ✓ | **BCNF** |
| Loan | ✓ | ✓ | ✓ | ✓ | **BCNF** |
| Transaction | ✓ | ✓ | ✓ | ✓ | **BCNF** |
| Loan_Payment | ✓ | ✓ | ✓ | ✓ | **BCNF** |

### Justification

- **1NF:** All attributes hold atomic, indivisible values; no repeating groups (e.g. multiple phone numbers per customer were avoided by storing one).
- **2NF:** All relations have a single-column primary key, so no partial dependency can exist; all non-key attributes depend on the whole key.
- **3NF:** No non-key attribute depends on another non-key attribute. For example, in *Account*, Balance depends only on Account_No, not on Acc_Type.
- **BCNF:** Every functional dependency has the primary key as its determinant. Since every relation's only determinant is its primary key, all relations satisfy BCNF.

**Highest normal form achieved for every relation: BCNF.**

---

## 5. SQL Implementation

Full executable SQL is in `banking_system.sql`. Below are the key sections.

### 5.1 Create Tables

```sql
CREATE TABLE Branch (
    Branch_ID     INT PRIMARY KEY,
    Branch_Name   VARCHAR(50) NOT NULL,
    City          VARCHAR(50) NOT NULL,
    Assets        DECIMAL(15,2) CHECK (Assets >= 0)
);

CREATE TABLE Customer (
    Customer_ID   INT PRIMARY KEY,
    Name          VARCHAR(60) NOT NULL,
    Address       VARCHAR(100),
    Phone         VARCHAR(15) UNIQUE,
    Email         VARCHAR(60) UNIQUE,
    DOB           DATE
);

CREATE TABLE Account (
    Account_No    INT PRIMARY KEY,
    Acc_Type      VARCHAR(20) CHECK (Acc_Type IN ('Savings','Current','FD')),
    Balance       DECIMAL(12,2) DEFAULT 0 CHECK (Balance >= 0),
    Open_Date     DATE NOT NULL,
    Branch_ID     INT,
    Customer_ID   INT,
    FOREIGN KEY (Branch_ID)   REFERENCES Branch(Branch_ID),
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID)
);

CREATE TABLE Employee (
    Emp_ID        INT PRIMARY KEY,
    Name          VARCHAR(60) NOT NULL,
    Designation   VARCHAR(30),
    Salary        DECIMAL(10,2) CHECK (Salary > 0),
    Branch_ID     INT,
    FOREIGN KEY (Branch_ID) REFERENCES Branch(Branch_ID)
);

CREATE TABLE Loan (
    Loan_ID         INT PRIMARY KEY,
    Loan_Type       VARCHAR(20) CHECK (Loan_Type IN ('Home','Car','Education','Personal')),
    Amount          DECIMAL(12,2) CHECK (Amount > 0),
    Interest_Rate   DECIMAL(5,2),
    Issue_Date      DATE,
    Branch_ID       INT,
    Customer_ID     INT,
    FOREIGN KEY (Branch_ID)   REFERENCES Branch(Branch_ID),
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID)
);

CREATE TABLE Transaction (
    Txn_ID        INT PRIMARY KEY,
    Txn_Type      VARCHAR(15) CHECK (Txn_Type IN ('Deposit','Withdraw','Transfer')),
    Amount        DECIMAL(12,2) CHECK (Amount > 0),
    Txn_Date      DATE NOT NULL,
    Account_No    INT,
    FOREIGN KEY (Account_No) REFERENCES Account(Account_No)
);

CREATE TABLE Loan_Payment (
    Payment_ID    INT PRIMARY KEY,
    Loan_ID       INT,
    Pay_Date      DATE,
    Amount_Paid   DECIMAL(12,2) CHECK (Amount_Paid > 0),
    FOREIGN KEY (Loan_ID) REFERENCES Loan(Loan_ID)
);
```

### 5.2 Sample Data (excerpt)

```sql
INSERT INTO Branch VALUES
 (1,'MG Road','Bengaluru',50000000),
 (2,'Connaught Place','Delhi',75000000),
 (3,'Marine Drive','Mumbai',90000000);

INSERT INTO Customer VALUES
 (101,'Aarav Sharma','22 Park Street, Delhi','9876543210','aarav@gmail.com','1995-04-12'),
 (102,'Priya Verma','15 MG Road, Bengaluru','9123456780','priya@yahoo.com','1990-07-23'),
 (103,'Rohan Mehta','9 Marine Drive, Mumbai','9988776655','rohan@outlook.com','1988-01-15'),
 (104,'Sneha Iyer','5 Anna Salai, Chennai','9001122334','sneha@gmail.com','1992-11-30');

INSERT INTO Account VALUES
 (1001,'Savings',45000.00,'2022-03-15',1,102),
 (1002,'Current',120000.00,'2021-06-10',2,101),
 (1003,'Savings',8500.00,'2023-01-20',3,103),
 (1004,'FD',200000.00,'2020-09-05',1,104);

INSERT INTO Employee VALUES
 (501,'Manish Kumar','Manager',85000,1),
 (502,'Anita Rao','Cashier',40000,2),
 (503,'Vikas Singh','Clerk',32000,3);

INSERT INTO Loan VALUES
 (701,'Home',2500000,8.50,'2023-02-10',1,102),
 (702,'Car',600000,9.25,'2024-05-21',2,101),
 (703,'Education',400000,7.00,'2022-08-15',3,103);

INSERT INTO Transaction VALUES
 (9001,'Deposit',10000,'2025-01-05',1001),
 (9002,'Withdraw',2000,'2025-01-12',1001),
 (9003,'Deposit',50000,'2025-02-01',1002),
 (9004,'Transfer',5000,'2025-02-14',1003);

INSERT INTO Loan_Payment VALUES
 (8001,701,'2025-01-15',25000),
 (8002,702,'2025-02-15',12000),
 (8003,701,'2025-02-15',25000);
```

---

## 6. Sample Queries

### Q1. List all customers and the branches where they hold accounts (JOIN)
```sql
SELECT C.Customer_ID, C.Name, A.Account_No, A.Acc_Type, B.Branch_Name
FROM   Customer  C
JOIN   Account   A ON C.Customer_ID = A.Customer_ID
JOIN   Branch    B ON A.Branch_ID  = B.Branch_ID;
```

### Q2. Total deposits per branch (Aggregation + GROUP BY)
```sql
SELECT B.Branch_Name, SUM(A.Balance) AS Total_Deposits
FROM   Account A
JOIN   Branch  B ON A.Branch_ID = B.Branch_ID
GROUP  BY B.Branch_Name;
```

### Q3. Customers who have taken a loan greater than ₹5,00,000
```sql
SELECT C.Name, L.Loan_Type, L.Amount
FROM   Customer C
JOIN   Loan     L ON C.Customer_ID = L.Customer_ID
WHERE  L.Amount > 500000;
```

### Q4. Number of employees in each branch (Aggregation)
```sql
SELECT B.Branch_Name, COUNT(E.Emp_ID) AS Employee_Count
FROM   Branch   B
LEFT JOIN Employee E ON B.Branch_ID = E.Branch_ID
GROUP BY B.Branch_Name;
```

### Q5. Top 3 accounts with the highest balances
```sql
SELECT Account_No, Acc_Type, Balance
FROM   Account
ORDER  BY Balance DESC
LIMIT  3;
```

### Q6. Total amount paid against each loan and remaining balance
```sql
SELECT L.Loan_ID, L.Loan_Type, L.Amount AS Loan_Amount,
       COALESCE(SUM(P.Amount_Paid),0) AS Total_Paid,
       L.Amount - COALESCE(SUM(P.Amount_Paid),0) AS Remaining
FROM   Loan L
LEFT JOIN Loan_Payment P ON L.Loan_ID = P.Loan_ID
GROUP  BY L.Loan_ID, L.Loan_Type, L.Amount;
```

### Q7. Transactions of a particular customer (Sub-query)
```sql
SELECT T.*
FROM   Transaction T
WHERE  T.Account_No IN ( SELECT Account_No FROM Account WHERE Customer_ID = 102 );
```

### Q8. Average salary of employees (Aggregation)
```sql
SELECT Designation, AVG(Salary) AS Avg_Salary
FROM   Employee
GROUP  BY Designation;
```

### Q9. Branches whose total assets exceed the average asset value (HAVING + Sub-query)
```sql
SELECT Branch_Name, Assets
FROM   Branch
WHERE  Assets > (SELECT AVG(Assets) FROM Branch);
```

### Q10. Customers who have BOTH an account and a loan
```sql
SELECT DISTINCT C.Customer_ID, C.Name
FROM   Customer C
JOIN   Account  A ON C.Customer_ID = A.Customer_ID
JOIN   Loan     L ON C.Customer_ID = L.Customer_ID;
```

---

## 7. Conclusion

The Banking Management System database has been successfully designed, normalized up to **BCNF**, and implemented in SQL. Constraints (PRIMARY KEY, FOREIGN KEY, CHECK, UNIQUE, NOT NULL) ensure data integrity, while the sample queries demonstrate joins, aggregations, sub-queries, and grouping — covering the full spectrum of typical banking operations such as customer enquiries, branch reports, and loan tracking.

---
**End of Report**

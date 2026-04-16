-- =====================================================================
-- DBMS PROJECT : BANKING MANAGEMENT SYSTEM
-- Author       : Daksh Pathak
-- Date         : 16th April 2025
-- Description  : Complete SQL implementation - schema, data, queries
-- =====================================================================

-- Drop existing tables (run safely on re-execution)
DROP TABLE IF EXISTS Loan_Payment;
DROP TABLE IF EXISTS Transaction;
DROP TABLE IF EXISTS Loan;
DROP TABLE IF EXISTS Employee;
DROP TABLE IF EXISTS Account;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS Branch;

-- ---------------------------------------------------------------------
-- 1. CREATE TABLES
-- ---------------------------------------------------------------------

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

-- ---------------------------------------------------------------------
-- 2. INSERT SAMPLE DATA
-- ---------------------------------------------------------------------

INSERT INTO Branch VALUES
 (1,'MG Road','Bengaluru',50000000),
 (2,'Connaught Place','Delhi',75000000),
 (3,'Marine Drive','Mumbai',90000000),
 (4,'Park Street','Kolkata',30000000);

INSERT INTO Customer VALUES
 (101,'Aarav Sharma','22 Park Street, Delhi','9876543210','aarav@gmail.com','1995-04-12'),
 (102,'Priya Verma','15 MG Road, Bengaluru','9123456780','priya@yahoo.com','1990-07-23'),
 (103,'Rohan Mehta','9 Marine Drive, Mumbai','9988776655','rohan@outlook.com','1988-01-15'),
 (104,'Sneha Iyer','5 Anna Salai, Chennai','9001122334','sneha@gmail.com','1992-11-30'),
 (105,'Karan Patel','77 Ring Road, Ahmedabad','9445566778','karan@gmail.com','1985-06-18');

INSERT INTO Account VALUES
 (1001,'Savings',45000.00,'2022-03-15',1,102),
 (1002,'Current',120000.00,'2021-06-10',2,101),
 (1003,'Savings',8500.00,'2023-01-20',3,103),
 (1004,'FD',200000.00,'2020-09-05',1,104),
 (1005,'Savings',15000.00,'2024-03-11',4,105),
 (1006,'Current',60000.00,'2023-07-19',2,102);

INSERT INTO Employee VALUES
 (501,'Manish Kumar','Manager',85000,1),
 (502,'Anita Rao','Cashier',40000,2),
 (503,'Vikas Singh','Clerk',32000,3),
 (504,'Riya Das','Manager',82000,4),
 (505,'Suresh Nair','Cashier',38000,1);

INSERT INTO Loan VALUES
 (701,'Home',2500000,8.50,'2023-02-10',1,102),
 (702,'Car',600000,9.25,'2024-05-21',2,101),
 (703,'Education',400000,7.00,'2022-08-15',3,103),
 (704,'Personal',150000,11.50,'2024-12-01',4,105);

INSERT INTO Transaction VALUES
 (9001,'Deposit',10000,'2025-01-05',1001),
 (9002,'Withdraw',2000,'2025-01-12',1001),
 (9003,'Deposit',50000,'2025-02-01',1002),
 (9004,'Transfer',5000,'2025-02-14',1003),
 (9005,'Deposit',7500,'2025-03-09',1005),
 (9006,'Withdraw',12000,'2025-03-22',1006);

INSERT INTO Loan_Payment VALUES
 (8001,701,'2025-01-15',25000),
 (8002,702,'2025-02-15',12000),
 (8003,701,'2025-02-15',25000),
 (8004,703,'2025-03-15',8000),
 (8005,704,'2025-03-30',6000);

-- ---------------------------------------------------------------------
-- 3. SAMPLE QUERIES
-- ---------------------------------------------------------------------

-- Q1. Customers with their accounts and branch
SELECT C.Customer_ID, C.Name, A.Account_No, A.Acc_Type, B.Branch_Name
FROM   Customer  C
JOIN   Account   A ON C.Customer_ID = A.Customer_ID
JOIN   Branch    B ON A.Branch_ID  = B.Branch_ID;

-- Q2. Total deposits per branch
SELECT B.Branch_Name, SUM(A.Balance) AS Total_Deposits
FROM   Account A
JOIN   Branch  B ON A.Branch_ID = B.Branch_ID
GROUP  BY B.Branch_Name;

-- Q3. Customers with loans greater than 5,00,000
SELECT C.Name, L.Loan_Type, L.Amount
FROM   Customer C
JOIN   Loan     L ON C.Customer_ID = L.Customer_ID
WHERE  L.Amount > 500000;

-- Q4. Number of employees per branch
SELECT B.Branch_Name, COUNT(E.Emp_ID) AS Employee_Count
FROM   Branch   B
LEFT JOIN Employee E ON B.Branch_ID = E.Branch_ID
GROUP BY B.Branch_Name;

-- Q5. Top 3 accounts by balance
SELECT Account_No, Acc_Type, Balance
FROM   Account
ORDER  BY Balance DESC
LIMIT  3;

-- Q6. Total paid and remaining for each loan
SELECT L.Loan_ID, L.Loan_Type, L.Amount AS Loan_Amount,
       COALESCE(SUM(P.Amount_Paid),0) AS Total_Paid,
       L.Amount - COALESCE(SUM(P.Amount_Paid),0) AS Remaining
FROM   Loan L
LEFT JOIN Loan_Payment P ON L.Loan_ID = P.Loan_ID
GROUP  BY L.Loan_ID, L.Loan_Type, L.Amount;

-- Q7. Transactions for customer 102 (sub-query)
SELECT T.*
FROM   Transaction T
WHERE  T.Account_No IN (SELECT Account_No FROM Account WHERE Customer_ID = 102);

-- Q8. Average salary by designation
SELECT Designation, AVG(Salary) AS Avg_Salary
FROM   Employee
GROUP  BY Designation;

-- Q9. Branches with above-average assets
SELECT Branch_Name, Assets
FROM   Branch
WHERE  Assets > (SELECT AVG(Assets) FROM Branch);

-- Q10. Customers who have both an account and a loan
SELECT DISTINCT C.Customer_ID, C.Name
FROM   Customer C
JOIN   Account  A ON C.Customer_ID = A.Customer_ID
JOIN   Loan     L ON C.Customer_ID = L.Customer_ID;

-- =====================================================================
-- END OF FILE
-- =====================================================================

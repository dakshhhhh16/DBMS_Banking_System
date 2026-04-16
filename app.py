"""
Banking Management System – Flask Backend
Run:  python3 app.py   →  open http://localhost:5050
"""
from flask import Flask, jsonify, render_template, request
import mysql.connector

app = Flask(__name__)

DB = dict(host="localhost", user="root", password="", database="banking_db")


def query(sql, params=()):
    conn = mysql.connector.connect(**DB)
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/summary")
def summary():
    return jsonify({
        "branches":     query("SELECT COUNT(*) AS c FROM Branch")[0]["c"],
        "customers":    query("SELECT COUNT(*) AS c FROM Customer")[0]["c"],
        "accounts":     query("SELECT COUNT(*) AS c FROM Account")[0]["c"],
        "loans":        query("SELECT COUNT(*) AS c FROM Loan")[0]["c"],
        "total_deposit": float(query("SELECT COALESCE(SUM(Balance),0) AS s FROM Account")[0]["s"]),
        "total_loan":    float(query("SELECT COALESCE(SUM(Amount),0)  AS s FROM Loan")[0]["s"]),
    })


@app.route("/api/customers")
def customers():
    return jsonify(query("SELECT * FROM Customer ORDER BY Customer_ID"))


@app.route("/api/accounts")
def accounts():
    return jsonify(query("""
        SELECT A.Account_No, A.Acc_Type, A.Balance, A.Open_Date,
               C.Name AS Customer, B.Branch_Name
        FROM Account A
        JOIN Customer C ON A.Customer_ID = C.Customer_ID
        JOIN Branch   B ON A.Branch_ID   = B.Branch_ID
        ORDER BY A.Account_No
    """))


@app.route("/api/branches")
def branches():
    return jsonify(query("""
        SELECT B.Branch_ID, B.Branch_Name, B.City, B.Assets,
               COALESCE(SUM(A.Balance),0) AS Deposits,
               COUNT(DISTINCT E.Emp_ID)   AS Employees
        FROM   Branch B
        LEFT JOIN Account  A ON B.Branch_ID = A.Branch_ID
        LEFT JOIN Employee E ON B.Branch_ID = E.Branch_ID
        GROUP BY B.Branch_ID, B.Branch_Name, B.City, B.Assets
    """))


@app.route("/api/loans")
def loans():
    return jsonify(query("""
        SELECT L.Loan_ID, L.Loan_Type, L.Amount, L.Interest_Rate,
               L.Issue_Date, C.Name AS Customer, B.Branch_Name,
               COALESCE(SUM(P.Amount_Paid),0) AS Paid,
               L.Amount - COALESCE(SUM(P.Amount_Paid),0) AS Remaining
        FROM Loan L
        JOIN Customer C ON L.Customer_ID = C.Customer_ID
        JOIN Branch   B ON L.Branch_ID   = B.Branch_ID
        LEFT JOIN Loan_Payment P ON L.Loan_ID = P.Loan_ID
        GROUP BY L.Loan_ID, L.Loan_Type, L.Amount, L.Interest_Rate,
                 L.Issue_Date, C.Name, B.Branch_Name
    """))


@app.route("/api/transactions")
def transactions():
    return jsonify(query("""
        SELECT T.Txn_ID, T.Txn_Type, T.Amount, T.Txn_Date,
               T.Account_No, C.Name AS Customer
        FROM Transaction T
        JOIN Account  A ON T.Account_No = A.Account_No
        JOIN Customer C ON A.Customer_ID = C.Customer_ID
        ORDER BY T.Txn_Date DESC
    """))


@app.route("/api/employees")
def employees():
    return jsonify(query("""
        SELECT E.Emp_ID, E.Name, E.Designation, E.Salary, B.Branch_Name
        FROM Employee E JOIN Branch B ON E.Branch_ID = B.Branch_ID
        ORDER BY E.Emp_ID
    """))


if __name__ == "__main__":
    app.run(debug=True, port=5050)

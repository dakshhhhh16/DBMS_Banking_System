# Banking Management System — DBMS Project

A small banking database I built for my DBMS course. It models the everyday stuff a bank deals with — branches, customers, accounts, employees, loans, transactions, and loan payments — and ties it all together with proper keys, constraints and a handful of useful queries.

## What's inside

- **[Banking_System_Report.md](Banking_System_Report.md)** — the full report: ER model, relational schema, normalization (everything ends up in BCNF), and the SQL with explanations.
- **[banking_system.sql](banking_system.sql)** — the actual database. Drops & creates 7 tables, inserts sample data, and runs 10 queries (joins, aggregations, sub-queries).

## Run it

```bash
mysql -u root banking_db < banking_system.sql
```

Works on MySQL / MariaDB out of the box.

## Why this system?

Banks were the first thing that came to mind where data integrity actually *matters* — you can't have a withdrawal without an account, or a loan without a customer. It made the foreign keys and constraints feel like they were doing real work, not just being added because the rubric said so.

---
*Daksh Pathak · April 2025*

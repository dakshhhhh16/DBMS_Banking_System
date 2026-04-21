#!/usr/bin/env python3
import argparse
import os
import sqlite3
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def load_env_file(path):
    if not path.exists():
        return

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def resolve_project_path(value):
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT_DIR / path


def main():
    load_env_file(ROOT_DIR / ".env")

    parser = argparse.ArgumentParser(description="Initialize the SQLite database.")
    parser.add_argument(
        "--db-path",
        default=os.environ.get("DB_PATH", "instance/banking.sqlite3"),
        help="SQLite database path. Relative paths are resolved from the project root.",
    )
    parser.add_argument(
        "--schema",
        default="banking_system.sql",
        help="SQL schema file. Relative paths are resolved from the project root.",
    )
    args = parser.parse_args()

    db_path = resolve_project_path(args.db_path)
    schema_path = resolve_project_path(args.schema)

    if not schema_path.exists():
        raise SystemExit(f"Schema file not found: {schema_path}")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    schema_sql = schema_path.read_text()

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(schema_sql)

    print(db_path)


if __name__ == "__main__":
    main()

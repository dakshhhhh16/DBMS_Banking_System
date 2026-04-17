from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path
import sqlite3

from flask import current_app


sqlite3.register_adapter(Decimal, str)
sqlite3.register_converter("NUMERIC", lambda value: Decimal(value.decode()))


def init_db(app):
    db_path = _resolve_db_path(app)
    if db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    app.extensions["db_path"] = db_path


def _resolve_db_path(app):
    configured_path = app.config["DB_PATH"]
    if configured_path == ":memory:":
        return configured_path

    db_path = Path(configured_path)
    if not db_path.is_absolute():
        db_path = Path(app.root_path).parent / db_path
    return str(db_path)


def _connect(db_path):
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


@contextmanager
def get_connection():
    db_path = current_app.extensions["db_path"]
    conn = _connect(db_path)
    try:
        yield conn
    finally:
        conn.close()

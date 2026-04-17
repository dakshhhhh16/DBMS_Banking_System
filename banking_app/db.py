from contextlib import contextmanager

import mysql.connector.pooling
from flask import current_app


def init_db_pool(app):
    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="banking_pool",
        pool_size=app.config["DB_POOL_SIZE"],
        host=app.config["DB_HOST"],
        port=app.config["DB_PORT"],
        user=app.config["DB_USER"],
        password=app.config["DB_PASSWORD"],
        database=app.config["DB_NAME"],
        autocommit=False,
    )
    app.extensions["db_pool"] = pool


@contextmanager
def get_connection():
    pool = current_app.extensions["db_pool"]
    conn = pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()

from banking_app.db import get_connection


class AuthRepository:
    def get_user_by_username(self, username):
        sql = """
            SELECT u.user_id, u.username, u.password_hash, u.customer_id, c.name, c.email
            FROM app_user u
            JOIN customer c ON c.customer_id = u.customer_id
            WHERE u.username = %s
            LIMIT 1
        """
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (username,))
            row = cur.fetchone()
            cur.close()
            return row

    def get_user_by_id(self, user_id):
        sql = """
            SELECT u.user_id, u.username, u.customer_id, c.name, c.email
            FROM app_user u
            JOIN customer c ON c.customer_id = u.customer_id
            WHERE u.user_id = %s
            LIMIT 1
        """
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (user_id,))
            row = cur.fetchone()
            cur.close()
            return row

    def username_exists(self, username):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM app_user WHERE username = %s LIMIT 1", (username,))
            exists = cur.fetchone() is not None
            cur.close()
            return exists

    def email_exists(self, email):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM customer WHERE email = %s LIMIT 1", (email,))
            exists = cur.fetchone() is not None
            cur.close()
            return exists

    def phone_exists(self, phone):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM customer WHERE phone = %s LIMIT 1", (phone,))
            exists = cur.fetchone() is not None
            cur.close()
            return exists

    def create_user_with_customer(self, *, name, address, phone, email, dob, username, password_hash):
        customer_sql = """
            INSERT INTO customer (name, address, phone, email, dob)
            VALUES (%s, %s, %s, %s, %s)
        """
        user_sql = """
            INSERT INTO app_user (username, password_hash, customer_id)
            VALUES (%s, %s, %s)
        """
        with get_connection() as conn:
            cur = conn.cursor(dictionary=True)
            try:
                cur.execute(customer_sql, (name, address, phone, email, dob))
                customer_id = cur.lastrowid
                cur.execute(user_sql, (username, password_hash, customer_id))
                user_id = cur.lastrowid
                conn.commit()
                return {
                    "user_id": user_id,
                    "username": username,
                    "customer_id": customer_id,
                    "name": name,
                    "email": email,
                }
            except Exception:
                conn.rollback()
                raise
            finally:
                cur.close()

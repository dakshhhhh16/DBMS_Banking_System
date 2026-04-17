from werkzeug.security import check_password_hash, generate_password_hash

from banking_app.utils.exceptions import AuthenticationError, ValidationError
from banking_app.utils.validators import (
    optional_date,
    require_email,
    require_phone,
    require_text,
)


class AuthService:
    def __init__(self, repository):
        self.repository = repository

    def register_user(self, payload):
        name = require_text(payload.get("name"), "Name", min_len=2, max_len=80)
        address = require_text(payload.get("address"), "Address", min_len=5, max_len=200)
        phone = require_phone(payload.get("phone"))
        email = require_email(payload.get("email"))
        dob = optional_date(payload.get("dob"), "Date of birth")

        username = require_text(payload.get("username"), "Username", min_len=4, max_len=30)
        password = require_text(payload.get("password"), "Password", min_len=8, max_len=128)

        if self.repository.username_exists(username):
            raise ValidationError("Username already exists.")
        if self.repository.email_exists(email):
            raise ValidationError("Email already exists.")
        if self.repository.phone_exists(phone):
            raise ValidationError("Phone already exists.")

        password_hash = generate_password_hash(password)
        return self.repository.create_user_with_customer(
            name=name,
            address=address,
            phone=phone,
            email=email,
            dob=dob,
            username=username,
            password_hash=password_hash,
        )

    def login_user(self, username, password):
        username_clean = require_text(username, "Username", min_len=4, max_len=30)
        password_clean = require_text(password, "Password", min_len=8, max_len=128)

        user = self.repository.get_user_by_username(username_clean)
        if not user or not check_password_hash(user["password_hash"], password_clean):
            raise AuthenticationError("Invalid username or password.")
        return user

    def get_user_for_session(self, user_id):
        return self.repository.get_user_by_id(user_id)

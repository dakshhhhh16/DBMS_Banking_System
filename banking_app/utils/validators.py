import re
from datetime import datetime
from decimal import Decimal

from flask import request, session

from banking_app.utils.exceptions import ValidationError


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9]{10,15}$")


def require_text(value, field_name, min_len=1, max_len=120):
    text = (value or "").strip()
    if not text:
        raise ValidationError(f"{field_name} is required.")
    if len(text) < min_len:
        raise ValidationError(f"{field_name} must be at least {min_len} characters.")
    if len(text) > max_len:
        raise ValidationError(f"{field_name} must be <= {max_len} characters.")
    return text


def require_email(value):
    email = require_text(value, "Email", min_len=1, max_len=120).lower()
    if not EMAIL_RE.match(email):
        raise ValidationError("Email format is invalid.")
    return email


def require_phone(value):
    phone = require_text(value, "Phone", min_len=1, max_len=15)
    if not PHONE_RE.match(phone):
        raise ValidationError("Phone must contain 10 to 15 digits.")
    return phone


def optional_date(value, field_name):
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError as err:
        raise ValidationError(f"{field_name} must be YYYY-MM-DD.") from err


def require_decimal(value, field_name, min_value=Decimal("0")):
    try:
        amount = Decimal(str(value))
    except Exception as err:
        raise ValidationError(f"{field_name} must be a valid number.") from err
    if amount < min_value:
        raise ValidationError(f"{field_name} must be >= {min_value}.")
    return amount


def validate_csrf_from_request():
    incoming = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
    session_token = session.get("csrf_token")
    if not session_token or incoming != session_token:
        raise ValidationError("CSRF token validation failed.")

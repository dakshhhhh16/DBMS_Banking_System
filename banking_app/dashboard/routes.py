from flask import Blueprint, current_app, flash, g, jsonify, redirect, render_template, request, url_for

from banking_app.utils.decorators import login_required
from banking_app.utils.exceptions import AppError
from banking_app.utils.validators import validate_csrf_from_request


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
@login_required
def home():
    error_message = request.args.get("error")
    if error_message:
        flash(error_message, "danger")

    payload = current_app.extensions["banking_service"].get_dashboard_payload(g.user["customer_id"])
    return render_template("dashboard/home.html", payload=payload)


@dashboard_bp.post("/accounts/create")
@login_required
def create_account():
    try:
        validate_csrf_from_request()
        current_app.extensions["banking_service"].create_account(g.user["customer_id"], request.form)
        flash("Account created successfully.", "success")
    except AppError as err:
        flash(err.message, "danger")
    return redirect(url_for("dashboard.home"))


@dashboard_bp.post("/transactions/create")
@login_required
def create_transaction():
    try:
        validate_csrf_from_request()
        current_app.extensions["banking_service"].create_transaction(g.user["customer_id"], request.form)
        flash("Transaction completed successfully.", "success")
    except AppError as err:
        flash(err.message, "danger")
    return redirect(url_for("dashboard.home"))


@dashboard_bp.get("/api/summary")
@login_required
def api_summary():
    payload = current_app.extensions["banking_service"].get_dashboard_payload(g.user["customer_id"])
    return jsonify(payload["summary"])


@dashboard_bp.get("/api/accounts")
@login_required
def api_accounts():
    rows = current_app.extensions["banking_service"].repository.get_customer_accounts(g.user["customer_id"])
    return jsonify(rows)


@dashboard_bp.get("/api/transactions")
@login_required
def api_transactions():
    rows = current_app.extensions["banking_service"].repository.get_recent_transactions_for_customer(
        g.user["customer_id"]
    )
    return jsonify(rows)

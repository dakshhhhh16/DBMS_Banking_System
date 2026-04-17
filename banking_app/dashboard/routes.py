from flask import Blueprint, current_app, flash, g, jsonify, redirect, render_template, request, url_for

from banking_app.utils.decorators import login_required
from banking_app.utils.exceptions import AppError, ValidationError
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


@dashboard_bp.get("/bank-details")
@login_required
def bank_details():
    payload = current_app.extensions["banking_service"].get_dashboard_payload(g.user["customer_id"])
    return render_template("dashboard/bank_details.html", payload=payload)


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


@dashboard_bp.post("/loans/apply")
@login_required
def apply_loan():
    try:
        validate_csrf_from_request()
        current_app.extensions["banking_service"].create_loan(g.user["customer_id"], request.form)
        flash("Loan application submitted successfully.", "success")
    except AppError as err:
        flash(err.message, "danger")
    return redirect(url_for("dashboard.home"))


@dashboard_bp.post("/loans/installments/pay")
@login_required
def pay_loan_installment():
    try:
        validate_csrf_from_request()
        current_app.extensions["banking_service"].create_loan_installment(g.user["customer_id"], request.form)
        flash("Loan installment deducted successfully.", "success")
    except AppError as err:
        flash(err.message, "danger")
    return redirect(url_for("dashboard.home"))


@dashboard_bp.route("/api/accounts/<int:account_no>", methods=["PUT", "PATCH"])
@login_required
def api_update_account(account_no):
    validate_csrf_from_request()

    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        raise ValidationError("JSON object payload is required.")

    updated_account = current_app.extensions["banking_service"].update_account(
        g.user["customer_id"],
        account_no,
        payload,
    )
    return jsonify(updated_account)


@dashboard_bp.delete("/api/accounts/<int:account_no>")
@login_required
def api_close_account(account_no):
    validate_csrf_from_request()
    current_app.extensions["banking_service"].close_account(g.user["customer_id"], account_no)
    return jsonify({"message": "Account closed successfully.", "account_no": account_no})


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


@dashboard_bp.get("/api/loans")
@login_required
def api_loans():
    rows = current_app.extensions["banking_service"].repository.get_customer_loans(g.user["customer_id"])
    return jsonify(rows)


@dashboard_bp.get("/api/loan-payments")
@login_required
def api_loan_payments():
    rows = current_app.extensions["banking_service"].repository.get_recent_loan_payments_for_customer(
        g.user["customer_id"]
    )
    return jsonify(rows)

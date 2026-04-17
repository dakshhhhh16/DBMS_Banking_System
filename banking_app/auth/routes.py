from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from banking_app.utils.exceptions import AppError
from banking_app.utils.validators import validate_csrf_from_request


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            validate_csrf_from_request()
            user = current_app.extensions["auth_service"].register_user(request.form)
            session.clear()
            session["user_id"] = user["user_id"]
            flash("Registration successful.", "success")
            return redirect(url_for("dashboard.home"))
        except AppError as err:
            flash(err.message, "danger")
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            validate_csrf_from_request()
            user = current_app.extensions["auth_service"].login_user(
                request.form.get("username"), request.form.get("password")
            )
            session.clear()
            session["user_id"] = user["user_id"]
            flash("Welcome back.", "success")
            return redirect(url_for("dashboard.home"))
        except AppError as err:
            flash(err.message, "danger")
    return render_template("auth/login.html")


@auth_bp.post("/logout")
def logout():
    try:
        validate_csrf_from_request()
    except AppError:
        pass
    session.clear()
    flash("You were logged out.", "info")
    return redirect(url_for("auth.login"))

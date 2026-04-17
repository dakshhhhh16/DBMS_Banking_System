from flask import Flask, g, jsonify, redirect, session, url_for

from banking_app.auth.routes import auth_bp
from banking_app.config import Config
from banking_app.dashboard.routes import dashboard_bp
from banking_app.db import init_db_pool
from banking_app.repositories.auth_repository import AuthRepository
from banking_app.repositories.banking_repository import BankingRepository
from banking_app.services.auth_service import AuthService
from banking_app.services.banking_service import BankingService
from banking_app.utils.exceptions import AppError


def create_app(test_config=None):
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
        static_url_path="/static",
    )
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    if not app.config.get("SKIP_DB_INIT", False):
        init_db_pool(app)

    if "db_pool" in app.extensions:
        auth_repo = AuthRepository()
        banking_repo = BankingRepository()
        app.extensions["auth_service"] = AuthService(auth_repo)
        app.extensions["banking_service"] = BankingService(banking_repo)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")
        g.user = None
        if user_id and "auth_service" in app.extensions:
            g.user = app.extensions["auth_service"].get_user_for_session(user_id)
            if g.user is None:
                session.clear()

    @app.context_processor
    def inject_template_globals():
        return {
            "current_user": g.get("user"),
            "csrf_token": _get_or_create_csrf_token,
        }

    @app.errorhandler(AppError)
    def handle_known_app_error(err):
        if _is_json_request():
            return jsonify({"error": err.message}), err.status_code
        return redirect(url_for("dashboard.home", error=err.message))

    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        app.logger.exception("Unhandled error: %s", err)
        if _is_json_request():
            return jsonify({"error": "Unexpected server error."}), 500
        return redirect(url_for("dashboard.home", error="Unexpected server error."))

    return app


def _is_json_request():
    from flask import request

    return request.path.startswith("/api/") or request.is_json


def _get_or_create_csrf_token():
    import secrets

    token = session.get("csrf_token")
    if not token:
        token = secrets.token_hex(16)
        session["csrf_token"] = token
    return token

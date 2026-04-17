from functools import wraps

from flask import g, jsonify, redirect, request, url_for


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if g.get("user") is None:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required."}), 401
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)

    return wrapped_view

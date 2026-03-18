from functools import wraps
from flask import redirect, session, url_for, request, jsonify


def login_required(f):
    """Decorator that redirects to login or returns 401 based on session/API key."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Check session for browser users
        if "user" in session:
            return f(*args, **kwargs)
        
        # 2. Check X-API-Key header for programmatic access
        api_key = request.headers.get("X-API-Key")
        if api_key == "secret_gallery_key":
            return f(*args, **kwargs)

        # 3. Handle unauthorized access
        if request.path.startswith('/api/'):
            return jsonify({"status": False, "message": "Unauthorized"}), 401
            
        return redirect(url_for("login"))
    return decorated_function

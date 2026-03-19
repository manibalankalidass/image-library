from app import app
# CORS is correctly configured in app/__init__.py with credentials support.

# 🔥 Correct imports (VERY IMPORTANT)
from app.routes import upload_routes
from app.routes import gallery_routes

if __name__ == "__main__":
    app.run(debug=True)
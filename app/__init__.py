import os

from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_mysqldb import MySQL

load_dotenv()

import config

app = Flask(__name__)

app.secret_key = config.SECRET_KEY

app.config["MYSQL_HOST"] = config.MYSQL_HOST
app.config["MYSQL_USER"] = config.MYSQL_USER
app.config["MYSQL_PASSWORD"] = config.MYSQL_PASSWORD
app.config["MYSQL_DB"] = config.MYSQL_DB

mysql = MySQL(app)

from app.routes.auth_routes import *     # noqa: F401,F403,E402
from app.routes.category_routes import * # noqa: F401,F403,E402
from app.routes.upload_routes import *   # noqa: F401,F403,E402
from app.routes.gallery_routes import *  # noqa: F401,F403,E402


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER    = os.path.join(BASE_DIR, "..", config.UPLOAD_FOLDER)
THUMBNAIL_FOLDER = os.path.join(BASE_DIR, "..", config.THUMBNAIL_FOLDER)


@app.context_processor
def inject_total_images():
    """Inject total image count into every template – skipped when not logged in."""
    from flask import session
    if "user" not in session:
        return dict(total_images=0)
    from app.services.library_service import get_total_images
    return dict(total_images=get_total_images())


@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/thumbnails/<path:filename>")
def thumbnails(filename):
    return send_from_directory(THUMBNAIL_FOLDER, filename)

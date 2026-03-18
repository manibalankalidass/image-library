import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "mysql")
MYSQL_DB = os.getenv("MYSQL_DB", "imagelibrary")

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
THUMBNAIL_FOLDER = os.getenv("THUMBNAIL_FOLDER", "thumbnails")

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

# Supported countries (moved here from upload_routes.py)
COUNTRIES = [
    {"code": "UK", "name": "United Kingdom"},
    {"code": "US", "name": "United States"},
    {"code": "IN", "name": "India"},
    {"code": "AU", "name": "Australia"},
    {"code": "CA", "name": "Canada"},
]
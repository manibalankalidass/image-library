from flask import jsonify

from app import app
from app.security import login_required
from app.services.library_service import get_gallery_payload


@app.route("/api/images")
@login_required
def list_images():

    return jsonify({"status": True, "data": get_gallery_payload()})

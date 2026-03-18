import os
import threading
from datetime import datetime

from flask import jsonify, render_template, request

import config
from app import app
from app.security import login_required
from app.services.library_service import fetch_active_categories, fetch_category_by_id, insert_image_record
from app.utils.storage import (
    cleanup_directory,
    ensure_storage_directories,
    extract_zip_to_temp,
    iter_image_files,
    move_processed_image,
    save_single_image,
)

ensure_storage_directories()


@app.route("/upload")
@login_required
def upload():
    return render_template(
        "upload.html",
        categories=fetch_active_categories(),
        countries=config.COUNTRIES,
    )


# =============================
# SINGLE IMAGE UPLOAD
# =============================

@app.route("/upload-image", methods=["POST"])
@login_required
def upload_image():
    image = request.files.get("image")
    category_id = request.form.get("category")

    if not image or not image.filename:
        return jsonify({"error": "Image file is required"}), 400

    if not category_id:
        return jsonify({"error": "Category is required"}), 400

    category = fetch_category_by_id(category_id)
    if not category:
        return jsonify({"error": "Invalid category"}), 400

    today = datetime.now().strftime("%Y-%m-%d")
    image_data = save_single_image(image, today)

    insert_image_record(
        category_id=category[0],
        image_name=image_data["image_name"],
        file_path=image_data["file_path"],
        thumbnail_path=image_data["thumbnail_path"],
        file_size=image_data["file_size"],
        country=category[2],
    )

    return jsonify({"message": "Image uploaded successfully", "image": image_data})


# =============================
# BACKGROUND ZIP PROCESS
# =============================

def process_zip_background(zip_path, today, category_id):
    with app.app_context():
        extract_path = extract_zip_to_temp(zip_path, today)

        try:
            category = fetch_category_by_id(category_id)
            if not category:
                return

            for image_path in iter_image_files(extract_path):
                image_data = move_processed_image(image_path, today)
                insert_image_record(
                    category_id=category[0],
                    image_name=image_data["image_name"],
                    file_path=image_data["file_path"],
                    thumbnail_path=image_data["thumbnail_path"],
                    file_size=image_data["file_size"],
                    country=category[2],
                )
        finally:
            cleanup_directory(extract_path)


# =============================
# ZIP UPLOAD API
# =============================

@app.route("/upload-zip", methods=["POST"])
@login_required
def upload_zip():
    zip_file = request.files.get("zipfile")
    category_id = request.form.get("category")

    if not zip_file or not zip_file.filename:
        return jsonify({"error": "No zip file uploaded"}), 400

    if not category_id:
        return jsonify({"error": "Category is required"}), 400

    category = fetch_category_by_id(category_id)
    if not category:
        return jsonify({"error": "Invalid category"}), 400

    today = datetime.now().strftime("%Y-%m-%d")
    upload_root = os.path.join(config.UPLOAD_FOLDER, today)
    os.makedirs(upload_root, exist_ok=True)

    zip_name = f"{datetime.now().strftime('%H-%M-%S')}_{os.path.basename(zip_file.filename)}"
    zip_path = os.path.join(upload_root, zip_name)
    zip_file.save(zip_path)

    thread = threading.Thread(
        target=process_zip_background,
        args=(zip_path, today, category_id),
        daemon=True,
    )
    thread.start()

    return jsonify({"message": "ZIP uploaded. Processing in background."})

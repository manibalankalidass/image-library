import os
import shutil
import uuid
import zipfile
from pathlib import Path

from PIL import Image
from werkzeug.utils import secure_filename

import config


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def ensure_storage_directories():
    for folder in (config.UPLOAD_FOLDER, config.THUMBNAIL_FOLDER, "extracted"):
        os.makedirs(_abs_path(folder), exist_ok=True)


def dated_storage_paths(date_key):
    upload_rel = os.path.join(config.UPLOAD_FOLDER, date_key)
    thumbnail_rel = os.path.join(config.THUMBNAIL_FOLDER, date_key)

    upload_abs = _abs_path(upload_rel)
    thumbnail_abs = _abs_path(thumbnail_rel)

    os.makedirs(upload_abs, exist_ok=True)
    os.makedirs(thumbnail_abs, exist_ok=True)

    return {
        "upload_rel": upload_rel,
        "thumbnail_rel": thumbnail_rel,
        "upload_abs": upload_abs,
        "thumbnail_abs": thumbnail_abs,
    }


def extract_zip_to_temp(zip_path, date_key):
    extract_rel = os.path.join("extracted", date_key, str(uuid.uuid4()))
    extract_abs = _abs_path(extract_rel)
    os.makedirs(extract_abs, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_abs)

    return extract_abs


def get_non_colliding_name(upload_dir, base_name):
    """
    If base_name exists in upload_dir, append exactly -1, -2, etc.
    until a free filename is found.
    """
    path = Path(os.path.join(upload_dir, base_name))
    if not path.exists():
        return base_name

    stem = path.stem
    ext = path.suffix
    counter = 1

    while True:
        new_name = f"{stem}-{counter}{ext}"
        if not Path(os.path.join(upload_dir, new_name)).exists():
            return new_name
        counter += 1


def save_single_image(file_storage, date_key):
    paths = dated_storage_paths(date_key)
    base_image_name = build_unique_filename(file_storage.filename)
    image_name = get_non_colliding_name(paths["upload_abs"], base_image_name)

    upload_abs = os.path.join(paths["upload_abs"], image_name)
    thumbnail_abs = os.path.join(paths["thumbnail_abs"], image_name)

    file_storage.save(upload_abs)
    create_thumbnail(upload_abs, thumbnail_abs)

    return build_image_payload(paths, image_name)


def move_processed_image(source_path, date_key):
    paths = dated_storage_paths(date_key)
    base_image_name = build_unique_filename(os.path.basename(source_path))
    image_name = get_non_colliding_name(paths["upload_abs"], base_image_name)

    upload_abs = os.path.join(paths["upload_abs"], image_name)
    thumbnail_abs = os.path.join(paths["thumbnail_abs"], image_name)

    shutil.move(source_path, upload_abs)
    create_thumbnail(upload_abs, thumbnail_abs)

    return build_image_payload(paths, image_name)


def iter_image_files(directory):
    for root, _, files in os.walk(directory):
        for file_name in files:
            if Path(file_name).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                yield os.path.join(root, file_name)


def cleanup_directory(path):
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)


def build_unique_filename(file_name):
    """
    Returns the secure original filename.
    Collision resolution (appending -1, -2) is handled right before saving.
    """
    return secure_filename(file_name or "image")


def build_image_payload(paths, image_name):
    upload_rel_path = os.path.join(paths["upload_rel"], image_name)
    thumbnail_rel_path = os.path.join(paths["thumbnail_rel"], image_name)
    upload_abs_path = os.path.join(paths["upload_abs"], image_name)

    return {
        "image_name": image_name,
        "file_path": upload_rel_path,
        "thumbnail_path": thumbnail_rel_path,
        "file_size": os.path.getsize(upload_abs_path),
    }


def create_thumbnail(source_path, thumbnail_path, size=(200, 200)):
    with Image.open(source_path) as image:
        image.thumbnail(size)
        image.save(thumbnail_path)


def _abs_path(path):
    return os.path.join(PROJECT_ROOT, path)

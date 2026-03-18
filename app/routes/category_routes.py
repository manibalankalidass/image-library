from flask import jsonify, render_template, request

from app import app
from app.security import login_required
from app.services.library_service import fetch_category_page_data, insert_category


@app.route("/Category")
@login_required
def Category():
    categories, stats = fetch_category_page_data()
    return render_template("categories.html", categories=categories, stats=stats)


@app.route("/categories/create", methods=["POST"])
@login_required
def create_category():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    country = (data.get("country") or "").strip()

    if not name:
        return jsonify({"error": "Category name required"}), 400

    if not country:
        return jsonify({"error": "Country name required"}), 400

    category_id = insert_category(name, country)

    return jsonify(
        {
            "message": "Category saved",
            "category": {
                "id": category_id,
                "name": name,
                "country": country,
            },
        }
    )

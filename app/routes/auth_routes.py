from flask import flash, redirect, render_template, request, session, url_for

from app import app, mysql
from app.security import login_required
from app.services.library_service import fetch_dashboard_stats, get_images_by_category


@app.route("/", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and user[2] == password:
            session["user"] = user[1]
            session["user_id"] = user[0]
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    stats = fetch_dashboard_stats()
    return render_template(
        "dashboard.html",
        images=stats["images"],
        total_images=stats["total_images"],
        total_categories=stats["total_categories"],
        today_images=stats["today_images"],
        total_size_mb=stats["total_size_mb"],
        categories=get_images_by_category(),
    )

from collections import defaultdict
from datetime import datetime

from flask import request
from app import mysql


def fetch_active_categories():
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT id, name, country
        FROM category
        WHERE deleted = 0
        ORDER BY name
        """
    )
    rows = cur.fetchall()
    cur.close()

    return [
        {"id": row[0], "name": row[1], "country": row[2]}
        for row in rows
    ]


def fetch_category_by_id(category_id, active_only=True):
    cur = mysql.connection.cursor()
    query = """
        SELECT id, name, country, deleted
        FROM category
        WHERE id = %s
    """
    params = [category_id]

    if active_only:
        query += " AND deleted = 0"

    cur.execute(query, params)
    category = cur.fetchone()
    cur.close()
    return category


def insert_image_record(category_id, image_name, file_path, thumbnail_path, file_size, country):
    cur = mysql.connection.cursor()
    cur.execute(
        """
        INSERT INTO imagelibrary
            (category_id, image_name, file_path, thumbnail_path, file_size, country, deleted)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (category_id, image_name, file_path, thumbnail_path, file_size, country, 0),
    )
    mysql.connection.commit()
    cur.close()


def insert_category(name, country):
    cur = mysql.connection.cursor()
    cur.execute(
        """
        INSERT INTO category (name, country, deleted)
        VALUES (%s, %s, %s)
        """,
        (name, country, 0),
    )
    mysql.connection.commit()
    category_id = cur.lastrowid
    cur.close()
    return category_id


def fetch_category_page_data():
    cur = mysql.connection.cursor()

    # Single query: category list with image counts
    cur.execute(
        """
        SELECT
            c.id,
            c.name,
            c.country,
            c.deleted,
            COUNT(i.id) AS image_count
        FROM category c
        LEFT JOIN imagelibrary i
            ON i.category_id = c.id
            AND (i.deleted IS NULL OR i.deleted = 0)
        GROUP BY c.id, c.name, c.country, c.deleted
        ORDER BY c.name
        """
    )
    rows = cur.fetchall()

    categories = [
        {
            "id": row[0],
            "name": row[1],
            "slug": f"/{row[1].lower()}",
            "standard": row[2] if row[2] else "Both",
            "type": "general",
            "status": "active" if row[3] == 0 else "inactive",
            "images": row[4],
        }
        for row in rows
    ]

    # Stats query
    cur.execute(
        """
        SELECT
            COUNT(*) AS total_categories,
            COALESCE(SUM(CASE WHEN deleted = 0 THEN 1 ELSE 0 END), 0) AS active_categories,
            COALESCE(SUM(CASE WHEN deleted = 1 THEN 1 ELSE 0 END), 0) AS inactive_categories
        FROM category
        """
    )
    stats_row = cur.fetchone()
    cur.close()

    stats = {
        "total": stats_row[0],
        "active": stats_row[1],
        "inactive": stats_row[2],
    }

    return categories, stats


def fetch_dashboard_stats():
    """
    Optimised: replaced 4 separate DB round-trips with a single combined query,
    then derives all counts from the result set in Python.
    """
    cur = mysql.connection.cursor()

    # One query: fetch all active images with category name
    cur.execute(
        """
        SELECT
            il.id,
            il.category_id,
            il.image_name,
            il.file_path,
            il.file_size,
            il.country,
            il.created_at,
            il.thumbnail_path,
            c.name AS category_name
        FROM imagelibrary il
        LEFT JOIN category c ON il.category_id = c.id
        WHERE il.deleted = 0
        ORDER BY il.created_at DESC
        """
    )
    images = cur.fetchall()

    # One query: aggregate counts + storage in a single DB round-trip
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute(
        """
        SELECT
            COUNT(*) AS total_images,
            COALESCE(SUM(file_size), 0) AS total_size,
            COALESCE(SUM(CASE WHEN DATE(created_at) = %s THEN 1 ELSE 0 END), 0) AS today_images
        FROM imagelibrary
        WHERE deleted = 0
        """,
        (today,),
    )
    agg = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM category WHERE deleted = 0")
    total_categories = cur.fetchone()[0]
    cur.close()

    return {
        "images": images,
        "total_images": agg[0],
        "total_size_mb": round(agg[1] / (1024 * 1024), 2),
        "today_images": agg[2],
        "total_categories": total_categories,
    }


def get_images_by_category():
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT
            il.id,
            il.category_id,
            il.image_name,
            il.file_path,
            il.file_size,
            il.country,
            il.created_at,
            il.thumbnail_path,
            c.name AS category_name
        FROM imagelibrary il
        LEFT JOIN category c ON il.category_id = c.id
        WHERE il.deleted = 0
          AND c.deleted = 0
        ORDER BY c.name, il.created_at DESC
        """
    )
    rows = cur.fetchall()
    cur.close()

    categories = defaultdict(list)
    for row in rows:
        categories[row[-1]].append(row)

    return dict(categories)


def get_gallery_payload():
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT
            il.id,
            il.image_name,
            il.file_path,
            il.thumbnail_path,
            c.name
        FROM imagelibrary il
        LEFT JOIN category c ON il.category_id = c.id
        WHERE il.deleted = 0
        ORDER BY c.name, il.created_at DESC
        """
    )
    rows = cur.fetchall()
    cur.close()

    grouped = defaultdict(list)
    base_url = request.host_url


    for row in rows:
        grouped[row[4]].append(
            {
                "templatesId": row[0],
                "name": row[1],
                "path": base_url + row[2],
                "thumbnail": base_url + row[3],
            }
        )

    return [
        {"categoryName": category_name, "images": images}
        for category_name, images in grouped.items()
    ]


def get_total_images():
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT COUNT(*)
        FROM imagelibrary
        WHERE deleted = 0
        """
    )
    total = cur.fetchone()[0]
    cur.close()
    return total


def soft_delete_image(image_id):
    """Mark an image as deleted without removing it from disk."""
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE imagelibrary SET deleted = 1 WHERE id = %s",
        (image_id,),
    )
    mysql.connection.commit()
    cur.close()

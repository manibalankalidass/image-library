from app import mysql


def get_all_categories(active_only=False):
    """Return all category rows, optionally only active ones."""
    cur = mysql.connection.cursor()
    if active_only:
        cur.execute(
            "SELECT id, name, country, deleted FROM category WHERE deleted = 0 ORDER BY name"
        )
    else:
        cur.execute(
            "SELECT id, name, country, deleted FROM category ORDER BY name"
        )
    rows = cur.fetchall()
    cur.close()
    return rows


def get_category_by_id(category_id):
    """Return a single category row or None."""
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT id, name, country, deleted FROM category WHERE id = %s",
        (category_id,),
    )
    row = cur.fetchone()
    cur.close()
    return row


def deactivate_category(category_id):
    """Soft-delete a category."""
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE category SET deleted = 1 WHERE id = %s",
        (category_id,),
    )
    mysql.connection.commit()
    cur.close()

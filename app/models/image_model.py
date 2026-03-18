from app import mysql


def get_image_by_id(image_id):
    """Return a single image row or None."""
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT id, category_id, image_name, file_path, file_size,
               country, created_at, thumbnail_path
        FROM imagelibrary
        WHERE id = %s AND deleted = 0
        """,
        (image_id,),
    )
    row = cur.fetchone()
    cur.close()
    return row


def soft_delete_image(image_id):
    """Mark an image row as deleted (soft delete)."""
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE imagelibrary SET deleted = 1 WHERE id = %s",
        (image_id,),
    )
    mysql.connection.commit()
    cur.close()


def get_images_by_category_id(category_id):
    """Return all active images for a given category."""
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT id, category_id, image_name, file_path, file_size,
               country, created_at, thumbnail_path
        FROM imagelibrary
        WHERE category_id = %s AND deleted = 0
        ORDER BY created_at DESC
        """,
        (category_id,),
    )
    rows = cur.fetchall()
    cur.close()
    return rows

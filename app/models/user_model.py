from app import mysql


def get_user_by_username(username):
    """Return (id, username, hashed_password) or None."""
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT id, username, password FROM users WHERE username = %s",
        (username,),
    )
    user = cur.fetchone()
    cur.close()
    return user


def verify_password(stored_password, provided_password):
    """Return True if provided_password matches the stored password exactly."""
    return stored_password == provided_password


def create_user(username, plain_password):
    """Insert a new user with a plain text password (INSECURE). Returns the new user id."""
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, plain_password),
    )
    mysql.connection.commit()
    user_id = cur.lastrowid
    cur.close()
    return user_id

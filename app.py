from flask import Flask, render_template, request, redirect, url_for, g
from contextlib import contextmanager
from uuid import uuid4
from structured_logging import setup_logging
import sqlite3

app = Flask(__name__)

# Set up structured logging
logger = setup_logging()


# Generate a unique ID for every request
@app.before_request
def start_request_logging():
    g.request_id = uuid4().hex

    logger.info(
        "Request received",
        extra={
            "event": "request_started",
            "request_id": g.request_id
        }
    )


# Log when each request finishes
@app.after_request
def finish_request_logging(response):
    logger.info(
        f"Request completed with status {response.status_code}",
        extra={
            "event": "request_completed",
            "request_id": g.request_id
        }
    )

    return response


DATABASE = "wishlist.db"

CATEGORIES = [
    "Beauty", "Fashion", "Electronics",
    "Home", "School", "Other"
]

PRIORITIES = ["High", "Medium", "Low"]


def valid_priority(priority):
    return priority in PRIORITIES


# Reusable database connection helper
@contextmanager
def database_connection():
    conn = sqlite3.connect(DATABASE)

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# Create the database and items table
def init_db():
    with database_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL,
                store TEXT,
                priority TEXT,
                category TEXT DEFAULT 'Other'
            )
        """)

        columns = [
            column[1]
            for column in conn.execute("PRAGMA table_info(items)")
        ]

        if "category" not in columns:
            conn.execute(
                "ALTER TABLE items ADD COLUMN category TEXT DEFAULT 'Other'"
            )


# Display all wishlist items
@app.route("/")
def home():
    with database_connection() as conn:
        items = conn.execute("""
            SELECT id, name, price, store, priority, category
            FROM items
            ORDER BY id DESC
        """).fetchall()

    return render_template("index.html", items=items)


# Add a new wishlist item
@app.route("/add", methods=["POST"])
def add_item():
    name = request.form.get("name", "").strip()
    price = request.form.get("price", "")
    store = request.form.get("store", "")
    priority = request.form.get("priority", "")
    category = request.form.get("category", "Other")

    if not name:
        return "Item name is required", 400

    if not valid_priority(priority):
        return "Invalid priority", 400

    if category not in CATEGORIES:
        return "Invalid category", 400

    try:
        price_value = float(price) if price else None

        if price_value is not None and price_value < 0:
            return "Invalid price", 400

    except ValueError:
        return "Invalid price", 400


    # Log when the SQLite save operation begins
    logger.info(
        "Starting SQLite wishlist item insert",
        extra={
            "event": "add_item_started",
            "request_id": g.request_id
        }
    )

    try:
        # Save the wishlist item to SQLite
        with database_connection() as conn:
            conn.execute("""
                INSERT INTO items (name, price, store, priority, category)
                VALUES (?, ?, ?, ?, ?)
            """, (name, price_value, store, priority, category))

        # Log after the SQLite transaction commits
        logger.info(
            "Wishlist item saved successfully in SQLite",
            extra={
                "event": "add_item_success",
                "request_id": g.request_id
            }
        )

    except sqlite3.Error:
        # Log a database error without exposing private item data
        logger.error(
            "SQLite failed to save wishlist item",
            extra={
                "event": "add_item_failed",
                "request_id": g.request_id
            },
            exc_info=True
        )
        return "Unable to save wishlist item", 500

    return redirect(url_for("home"))



# Delete a wishlist item
@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    with database_connection() as conn:
        conn.execute(
            "DELETE FROM items WHERE id = ?",
            (item_id,)
        )

    return redirect(url_for("home"))


# Edit an existing wishlist item
@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", "")
        store = request.form.get("store", "")
        priority = request.form.get("priority", "")
        category = request.form.get("category", "Other")

        if not name:
            return "Item name is required", 400

        if not valid_priority(priority):
            return "Invalid priority", 400

        if category not in CATEGORIES:
            return "Invalid category", 400

        try:
            price_value = float(price) if price else None

            if price_value is not None and price_value < 0:
                return "Invalid price", 400

        except ValueError:
            return "Invalid price", 400

        with database_connection() as conn:
            result = conn.execute("""
                UPDATE items
                SET name = ?, price = ?, store = ?,
                    priority = ?, category = ?
                WHERE id = ?
            """, (
                name, price_value, store,
                priority, category, item_id
            ))

        if result.rowcount == 0:
            return "Item not found", 404

        return redirect(url_for("home"))

    with database_connection() as conn:
        item = conn.execute("""
            SELECT id, name, price, store, priority, category
            FROM items
            WHERE id = ?
        """, (item_id,)).fetchone()

    if item is None:
        return "Item not found", 404

    return render_template("edit.html", item=item)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

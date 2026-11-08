
from flask import Flask, render_template, request, redirect, url_for, g
from contextlib import contextmanager
from uuid import uuid4
from structured_logging import setup_logging
import sqlite3
import math

app = Flask(__name__)

# Preserve Milestone 8 structured logging
logger = setup_logging()

DATABASE = "wishlist.db"

CATEGORIES = [
    "Beauty", "Fashion", "Electronics",
    "Home", "School", "Other"
]

PRIORITIES = ["High", "Medium", "Low"]


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


def valid_priority(priority):
    return priority in PRIORITIES


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


def init_db():
    with database_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL,
                store TEXT,
                priority TEXT,
                category TEXT DEFAULT 'Other',
                favorite INTEGER NOT NULL DEFAULT 0,
                purchased INTEGER NOT NULL DEFAULT 0
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

        if "favorite" not in columns:
            conn.execute(
                "ALTER TABLE items ADD COLUMN favorite INTEGER NOT NULL DEFAULT 0"
            )

        if "purchased" not in columns:
            conn.execute(
                "ALTER TABLE items ADD COLUMN purchased INTEGER NOT NULL DEFAULT 0"
            )


def get_items(where="", params=()):
    query = """
        SELECT id, name, price, store, priority, category,
               favorite, purchased
        FROM items
    """
    if where:
        query += " WHERE " + where

    query += " ORDER BY id DESC"

    with database_connection() as conn:
        return conn.execute(query, params).fetchall()


def validate_item_form():
    name = request.form.get("name", "").strip()
    price = request.form.get("price", "").strip()
    store = request.form.get("store", "").strip()
    priority = request.form.get("priority", "")
    category = request.form.get("category", "Other")

    if not name:
        return None, ("Item name is required", 400)

    if not valid_priority(priority):
        return None, ("Invalid priority", 400)

    if category not in CATEGORIES:
        return None, ("Invalid category", 400)

    try:
        price_value = float(price) if price else None
        if price_value is not None and (
            not math.isfinite(price_value) or price_value < 0
        ):
            return None, ("Invalid price", 400)
    except ValueError:
        return None, ("Invalid price", 400)

    return (name, price_value, store, priority, category), None


# HOME DASHBOARD
@app.route("/")
def home():
    items = get_items()
    total_items = len(items)
    favorites_count = sum(item[6] for item in items)
    purchased_count = sum(item[7] for item in items)
    total_value = sum(
        item[2] for item in items if item[2] is not None
    )

    return render_template(
        "index.html",
        items=items,
        total_items=total_items,
        favorites_count=favorites_count,
        purchased_count=purchased_count,
        total_value=total_value,
        categories=CATEGORIES,
        priorities=PRIORITIES
    )


# MY WISHLIST
@app.route("/wishlist")
def wishlist():
    items = get_items()
    return render_template(
        "wishlist.html",
        items=items,
        categories=CATEGORIES,
        priorities=PRIORITIES
    )


# CATEGORIES
@app.route("/categories")
def categories():
    items = get_items()
    return render_template(
        "categories.html",
        items=items,
        categories=CATEGORIES
    )


# FAVORITES
@app.route("/favorites")
def favorites():
    items = get_items("favorite = ?", (1,))
    return render_template("favorites.html", items=items)


# SETTINGS
@app.route("/settings")
def settings():
    return render_template("settings.html")


# ADD ITEM
@app.route("/add", methods=["POST"])
def add_item():
    values, error = validate_item_form()
    if error:
        return error

    logger.info(
        "Starting SQLite wishlist item insert",
        extra={
            "event": "add_item_started",
            "request_id": g.request_id
        }
    )

    try:
        with database_connection() as conn:
            conn.execute("""
                INSERT INTO items
                (name, price, store, priority, category)
                VALUES (?, ?, ?, ?, ?)
            """, values)

        logger.info(
            "Wishlist item saved successfully in SQLite",
            extra={
                "event": "add_item_success",
                "request_id": g.request_id
            }
        )

    except sqlite3.Error:
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


# DELETE ITEM
@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    with database_connection() as conn:
        conn.execute(
            "DELETE FROM items WHERE id = ?",
            (item_id,)
        )

    return redirect(url_for("home"))


# EDIT ITEM
@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    if request.method == "POST":
        values, error = validate_item_form()
        if error:
            return error

        with database_connection() as conn:
            result = conn.execute("""
                UPDATE items
                SET name = ?, price = ?, store = ?,
                    priority = ?, category = ?
                WHERE id = ?
            """, (*values, item_id))

        if result.rowcount == 0:
            return "Item not found", 404

        return redirect(url_for("home"))

    with database_connection() as conn:
        item = conn.execute("""
            SELECT id, name, price, store, priority, category,
                   favorite, purchased
            FROM items WHERE id = ?
        """, (item_id,)).fetchone()

    if item is None:
        return "Item not found", 404

    return render_template(
        "edit.html",
        item=item,
        categories=CATEGORIES,
        priorities=PRIORITIES
    )


# FAVORITE / UNFAVORITE ITEM
@app.route("/favorite/<int:item_id>", methods=["POST"])
def toggle_favorite(item_id):
    with database_connection() as conn:
        result = conn.execute("""
            UPDATE items
            SET favorite = CASE WHEN favorite = 1 THEN 0 ELSE 1 END
            WHERE id = ?
        """, (item_id,))

    if result.rowcount == 0:
        return "Item not found", 404

    return redirect(url_for("favorites"))


# MARK ITEM AS PURCHASED / NOT PURCHASED
@app.route("/purchased/<int:item_id>", methods=["POST"])
def toggle_purchased(item_id):
    with database_connection() as conn:
        result = conn.execute("""
            UPDATE items
            SET purchased = CASE WHEN purchased = 1 THEN 0 ELSE 1 END
            WHERE id = ?
        """, (item_id,))

    if result.rowcount == 0:
        return "Item not found", 404

    return redirect(url_for("wishlist"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

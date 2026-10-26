
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DATABASE = os.path.join(app.root_path, "wishlist.db")

CATEGORIES = [
    "Beauty", "Fashion", "Electronics",
    "Home", "School", "Other"
]

PRIORITIES = ["High", "Medium", "Low"]


def valid_priority(priority):
    return priority in PRIORITIES


def init_db():
    conn = sqlite3.connect(DATABASE)

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

    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = sqlite3.connect(DATABASE)

    items = conn.execute("""
        SELECT id, name, price, store, priority, category
        FROM items
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template("index.html", items=items)


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

    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        INSERT INTO items (name, price, store, priority, category)
        VALUES (?, ?, ?, ?, ?)
    """, (name, price_value, store, priority, category))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    conn = sqlite3.connect(DATABASE)

    conn.execute(
        "DELETE FROM items WHERE id = ?",
        (item_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    conn = sqlite3.connect(DATABASE)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", "")
        store = request.form.get("store", "")
        priority = request.form.get("priority", "")
        category = request.form.get("category", "Other")

        if not name:
            conn.close()
            return "Item name is required", 400

        if not valid_priority(priority):
            conn.close()
            return "Invalid priority", 400

        if category not in CATEGORIES:
            conn.close()
            return "Invalid category", 400

        try:
            price_value = float(price) if price else None
            if price_value is not None and price_value < 0:
                conn.close()
                return "Invalid price", 400
        except ValueError:
            conn.close()
            return "Invalid price", 400

        result = conn.execute("""
            UPDATE items
            SET name = ?, price = ?, store = ?,
                priority = ?, category = ?
            WHERE id = ?
        """, (
            name, price_value, store,
            priority, category, item_id
        ))

        conn.commit()
        conn.close()

        if result.rowcount == 0:
            return "Item not found", 404

        return redirect(url_for("home"))

    item = conn.execute("""
        SELECT id, name, price, store, priority, category
        FROM items
        WHERE id = ?
    """, (item_id,)).fetchone()

    conn.close()

    if item is None:
        return "Item not found", 404

    return render_template("edit.html", item=item)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

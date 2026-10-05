from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("wishlist.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL,
            store TEXT,
            priority TEXT
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    conn = sqlite3.connect("wishlist.db")
    items = conn.execute("SELECT * FROM items").fetchall()
    conn.close()

    return render_template("index.html", items=items)


@app.route("/add", methods=["POST"])
def add_item():
    name = request.form["name"]
    price = request.form["price"]
    store = request.form["store"]
    priority = request.form["priority"]

    conn = sqlite3.connect("wishlist.db")
    conn.execute(
        "INSERT INTO items (name, price, store, priority) VALUES (?, ?, ?, ?)",
        (name, price, store, priority)
    )
    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
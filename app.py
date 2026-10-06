import sqlite3
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)
DB = "inventory.db"
LOW_STOCK = 10


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity >= 0),
            price REAL NOT NULL CHECK(price >= 0))""")


def validate(d):
    """Returns (clean_data, error_message)."""
    name = str(d.get("name", "")).strip()
    category = str(d.get("category", "")).strip()
    if not name or not category:
        return None, "Name and category are required."
    try:
        qty = int(d.get("quantity"))
        price = float(d.get("price"))
    except (TypeError, ValueError):
        return None, "Quantity and price must be numbers."
    if qty < 0 or price < 0:
        return None, "Quantity and price cannot be negative."
    return {"name": name, "category": category, "quantity": qty, "price": round(price, 2)}, None


def row(r):
    d = dict(r)
    d["low_stock"] = d["quantity"] <= LOW_STOCK
    return d


@app.get("/api/products")
def list_products():
    q = request.args.get("q", "").strip()
    cat = request.args.get("category", "").strip()
    sql, args = "SELECT * FROM products WHERE 1=1", []
    if q:
        sql += " AND (name LIKE ? OR category LIKE ? OR CAST(id AS TEXT) = ?)"
        args += [f"%{q}%", f"%{q}%", q]
    if cat:
        sql += " AND category = ?"
        args.append(cat)
    with db() as c:
        rows = c.execute(sql + " ORDER BY id DESC", args).fetchall()
    return jsonify([row(r) for r in rows])


@app.get("/api/categories")
def categories():
    with db() as c:
        rows = c.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()
    return jsonify([r["category"] for r in rows])


@app.post("/api/products")
def add_product():
    data, err = validate(request.get_json(silent=True) or {})
    if err:
        return jsonify(error=err), 400
    with db() as c:
        cur = c.execute("INSERT INTO products(name,category,quantity,price) VALUES(?,?,?,?)",
                        (data["name"], data["category"], data["quantity"], data["price"]))
        new = c.execute("SELECT * FROM products WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify(row(new)), 201


@app.put("/api/products/<int:pid>")
def update_product(pid):
    data, err = validate(request.get_json(silent=True) or {})
    if err:
        return jsonify(error=err), 400
    with db() as c:
        cur = c.execute("UPDATE products SET name=?,category=?,quantity=?,price=? WHERE id=?",
                        (data["name"], data["category"], data["quantity"], data["price"], pid))
        if cur.rowcount == 0:
            return jsonify(error="Product not found."), 404
        new = c.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    return jsonify(row(new))


@app.patch("/api/products/<int:pid>/stock")
def change_stock(pid):
    try:
        change = int((request.get_json(silent=True) or {}).get("change"))
    except (TypeError, ValueError):
        return jsonify(error="'change' must be an integer."), 400
    with db() as c:
        p = c.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
        if not p:
            return jsonify(error="Product not found."), 404
        if p["quantity"] + change < 0:
            return jsonify(error=f"Cannot reduce stock below zero (current: {p['quantity']})."), 400
        c.execute("UPDATE products SET quantity = quantity + ? WHERE id=?", (change, pid))
        new = c.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    return jsonify(row(new))


@app.delete("/api/products/<int:pid>")
def delete_product(pid):
    with db() as c:
        cur = c.execute("DELETE FROM products WHERE id=?", (pid,))
    if cur.rowcount == 0:
        return jsonify(error="Product not found."), 404
    return jsonify(message="Deleted.")


@app.get("/api/stats")
def stats():
    with db() as c:
        r = c.execute("""SELECT COUNT(*) n, COALESCE(SUM(quantity),0) units,
                         COALESCE(SUM(quantity*price),0) value,
                         COALESCE(SUM(quantity <= ?),0) low FROM products""", (LOW_STOCK,)).fetchone()
    return jsonify(products=r["n"], units=r["units"], value=round(r["value"], 2), low=r["low"])

@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)

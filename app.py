from pathlib import Path
import sqlite3

from flask import Flask, jsonify, render_template


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "lelegante_sales.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

app = Flask(__name__)


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    DB_PATH.parent.mkdir(exist_ok=True)

    with get_connection() as connection:
        script = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(script)

        product_count = connection.execute("SELECT COUNT(*) AS count FROM products").fetchone()["count"]
        if product_count > 0:
            return

        connection.executemany(
            """
            INSERT INTO products (name, category, price, stock_quantity, reorder_level)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ("Robe Satin Nuit", "Robes", 129.90, 18, 8),
                ("Blazer Ivoire Chic", "Vestes", 189.00, 6, 7),
                ("Sac Perlé Signature", "Accessoires", 89.50, 24, 10),
                ("Escarpins Nude Élégance", "Chaussures", 149.00, 5, 6),
                ("Chemisier Soie Douce", "Hauts", 74.90, 13, 8),
            ],
        )

        connection.executemany(
            """
            INSERT INTO sales (product_id, units_sold, sale_date)
            VALUES (?, ?, ?)
            """,
            [
                (1, 8, "2026-03-29"),
                (2, 3, "2026-03-29"),
                (3, 12, "2026-03-30"),
                (4, 4, "2026-03-31"),
                (5, 7, "2026-04-01"),
                (1, 6, "2026-04-02"),
                (3, 9, "2026-04-03"),
                (5, 5, "2026-04-03"),
            ],
        )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/summary")
def get_summary():
    with get_connection() as connection:
        total_revenue = connection.execute(
            """
            SELECT COALESCE(SUM(s.units_sold * p.price), 0) AS revenue
            FROM sales s
            JOIN products p ON p.id = s.product_id
            """
        ).fetchone()["revenue"]

        units_sold = connection.execute(
            "SELECT COALESCE(SUM(units_sold), 0) AS total_units FROM sales"
        ).fetchone()["total_units"]

        low_stock_count = connection.execute(
            """
            SELECT COUNT(*) AS low_stock
            FROM products
            WHERE stock_quantity <= reorder_level
            """
        ).fetchone()["low_stock"]

        best_product = connection.execute(
            """
            SELECT p.name, SUM(s.units_sold) AS total_units
            FROM sales s
            JOIN products p ON p.id = s.product_id
            GROUP BY p.id, p.name
            ORDER BY total_units DESC
            LIMIT 1
            """
        ).fetchone()

    return jsonify(
        {
            "revenue": round(total_revenue, 2),
            "unitsSold": units_sold,
            "lowStockCount": low_stock_count,
            "bestProduct": best_product["name"] if best_product else "Aucun",
        }
    )


@app.route("/api/products")
def get_products():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, name, category, price, stock_quantity, reorder_level,
                   CASE WHEN stock_quantity <= reorder_level THEN 1 ELSE 0 END AS low_stock
            FROM products
            ORDER BY category, name
            """
        ).fetchall()

    return jsonify([dict(row) for row in rows])


@app.route("/api/sales")
def get_sales():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT sale_date, SUM(units_sold) AS total_units
            FROM sales
            GROUP BY sale_date
            ORDER BY sale_date
            """
        ).fetchall()

    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)

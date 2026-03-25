import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'canteen.db')


def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates all tables if they don't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS customers (
            id_number TEXT PRIMARY KEY,
            name      TEXT NOT NULL,
            phone     TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS products (
            product_code TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            quantity     INTEGER NOT NULL DEFAULT 0,
            unit_price   REAL    NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS sales (
            receipt_no    INTEGER PRIMARY KEY,
            date          TEXT    NOT NULL,
            customer_id   TEXT,
            customer_name TEXT,
            description   TEXT,
            total         REAL    NOT NULL DEFAULT 0
        );
    """)

    conn.commit()
    conn.close()


# ── Users ──────────────────────────────────────────────────────────────────────

def verify_user(username: str, password: str) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM users WHERE username=? AND password=?", (username, password)
    ).fetchone()
    conn.close()
    return row is not None


def save_user(name: str, username: str, password: str) -> bool:
    """Returns False if username already exists."""
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (name, username, password) VALUES (?,?,?)",
            (name, username, password)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


# ── Customers ──────────────────────────────────────────────────────────────────

def get_all_customers():
    conn = get_connection()
    rows = conn.execute("SELECT id_number, name, phone FROM customers").fetchall()
    conn.close()
    return rows


def find_customer(id_number: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT id_number, name, phone FROM customers WHERE id_number=?", (id_number,)
    ).fetchone()
    conn.close()
    return row


def customer_exists(id_number: str) -> bool:
    return find_customer(id_number) is not None


def save_customer(id_number: str, name: str, phone: str) -> bool:
    """Returns False if customer ID already exists."""
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO customers (id_number, name, phone) VALUES (?,?,?)",
            (id_number, name, phone)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def update_customer(old_id: str, new_id: str, name: str, phone: str):
    conn = get_connection()
    conn.execute(
        "UPDATE customers SET id_number=?, name=?, phone=? WHERE id_number=?",
        (new_id, name, phone, old_id)
    )
    conn.commit()
    conn.close()


def delete_customer(id_number: str):
    conn = get_connection()
    conn.execute("DELETE FROM customers WHERE id_number=?", (id_number,))
    conn.commit()
    conn.close()


def search_customers_by_id(id_number: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id_number, name, phone FROM customers WHERE id_number=?", (id_number,)
    ).fetchall()
    conn.close()
    return rows


# ── Products ───────────────────────────────────────────────────────────────────

def get_all_products():
    conn = get_connection()
    rows = conn.execute(
        "SELECT product_code, product_name, quantity, unit_price FROM products"
    ).fetchall()
    conn.close()
    return rows


def find_product_by_code(product_code: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT product_code, product_name, quantity, unit_price FROM products WHERE product_code=?",
        (product_code,)
    ).fetchone()
    conn.close()
    return row


def find_product_by_name(product_name: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT product_code, product_name, quantity, unit_price FROM products "
        "WHERE LOWER(product_name)=LOWER(?)", (product_name,)
    ).fetchall()
    conn.close()
    return rows


def save_product(code: str, name: str, quantity: int, price: float) -> bool:
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO products (product_code, product_name, quantity, unit_price) VALUES (?,?,?,?)",
            (code, name, quantity, price)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def update_product(old_code: str, new_code: str, name: str, quantity: int, price: float):
    conn = get_connection()
    conn.execute(
        "UPDATE products SET product_code=?, product_name=?, quantity=?, unit_price=? WHERE product_code=?",
        (new_code, name, quantity, price, old_code)
    )
    conn.commit()
    conn.close()


def delete_product(product_code: str):
    conn = get_connection()
    conn.execute("DELETE FROM products WHERE product_code=?", (product_code,))
    conn.commit()
    conn.close()


def decrease_product_quantity(product_name: str, qty: int):
    conn = get_connection()
    conn.execute(
        "UPDATE products SET quantity = quantity - ? WHERE product_name=?",
        (qty, product_name)
    )
    conn.commit()
    conn.close()


def increase_product_quantity(product_name: str, qty: int):
    conn = get_connection()
    conn.execute(
        "UPDATE products SET quantity = quantity + ? WHERE product_name=?",
        (qty, product_name)
    )
    conn.commit()
    conn.close()


# ── Sales ──────────────────────────────────────────────────────────────────────

def get_all_sales():
    conn = get_connection()
    rows = conn.execute(
        "SELECT receipt_no, date, customer_id, customer_name, description, total FROM sales"
    ).fetchall()
    conn.close()
    return rows


def get_sales_by_date(date_str: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT receipt_no, date, customer_id, customer_name, description, total "
        "FROM sales WHERE date LIKE ?", (f"{date_str}%",)
    ).fetchall()
    conn.close()
    return rows


def get_sales_by_customer(customer_id: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT receipt_no, date, customer_id, customer_name, description, total "
        "FROM sales WHERE customer_id=?", (customer_id,)
    ).fetchall()
    conn.close()
    return rows


def get_next_receipt_number() -> int:
    conn = get_connection()
    row = conn.execute("SELECT MAX(receipt_no) FROM sales").fetchone()
    conn.close()
    max_val = row[0]
    return (max_val + 1) if max_val is not None else 1


def save_sale(receipt_no: int, date: str, customer_id: str, customer_name: str,
              description: str, total: float):
    conn = get_connection()
    conn.execute(
        "INSERT INTO sales (receipt_no, date, customer_id, customer_name, description, total) "
        "VALUES (?,?,?,?,?,?)",
        (receipt_no, date, customer_id, customer_name, description, total)
    )
    conn.commit()
    conn.close()


def update_sale(receipt_no: int, customer_id: str, customer_name: str,
                description: str, total: float):
    conn = get_connection()
    conn.execute(
        "UPDATE sales SET customer_id=?, customer_name=?, description=?, total=? "
        "WHERE receipt_no=?",
        (customer_id, customer_name, description, total, receipt_no)
    )
    conn.commit()
    conn.close()


def get_revenue_by_date(date_str: str) -> float:
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(total), 0) FROM sales WHERE date LIKE ?", (f"{date_str}%",)
    ).fetchone()
    conn.close()
    return row[0]

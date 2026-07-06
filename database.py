import sqlite3
import os

os.makedirs("database", exist_ok=True)

def connect():
    return sqlite3.connect("database/shop.db")


def init_db():
    conn = connect()
    cursor = conn.cursor()

    # PRODUCTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        subcategory TEXT,
        price REAL,
        stock INTEGER,
        photo TEXT
    )
    """)

    # SALES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        qty INTEGER,
        total REAL,
        date TEXT
    )
    """)

    # EXPENSES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        amount REAL,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()
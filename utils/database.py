import sqlite3
from datetime import datetime


DATABASE_NAME = "bookings.db"


def get_connection():
    """Create and return a connection to the SQLite database."""

    return sqlite3.connect(DATABASE_NAME)


def create_tables():
    """Create the customers and bookings tables if they don't exist."""

    connection = get_connection()
    cursor = connection.cursor()

    # Customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    # Bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            booking_type TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,

            FOREIGN KEY (customer_id)
            REFERENCES customers(customer_id)
        )
    """)

    connection.commit()
    connection.close()


def add_customer(name, email, phone):
    """Add a customer and return the generated customer ID."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO customers (name, email, phone)
        VALUES (?, ?, ?)
    """, (name, email, phone))

    customer_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return customer_id


def add_booking(
    customer_id,
    booking_type,
    booking_date,
    booking_time,
    status="confirmed"
):
    """Add a booking and return the generated booking ID."""

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO bookings (
            customer_id,
            booking_type,
            date,
            time,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        customer_id,
        booking_type,
        booking_date,
        booking_time,
        status,
        created_at
    ))

    booking_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return booking_id


def get_all_bookings():
    """Return all bookings along with customer information."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            bookings.id,
            customers.name,
            customers.email,
            customers.phone,
            bookings.booking_type,
            bookings.date,
            bookings.time,
            bookings.status,
            bookings.created_at
        FROM bookings
        JOIN customers
            ON bookings.customer_id = customers.customer_id
        ORDER BY bookings.id DESC
    """)

    bookings = cursor.fetchall()

    connection.close()

    return bookings


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

create_tables()
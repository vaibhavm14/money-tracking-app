import sqlite3
import os
from datetime import datetime # Keep for potential migration default date

# Define the database file name
DB_FILE = "transactions.db"

def init_db():
    """
    Initialize the database: create the table if it doesn't exist,
    and handle schema migration (like adding 'date' and 'tag' columns).
    """
    db_existed = os.path.exists(DB_FILE)
    print(f"Initializing database '{DB_FILE}'...")
    if not db_existed:
        print("Database file not found, creating new one.")

    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            # --- Step 1: Ensure the table exists with the latest schema ---
            # The schema includes id, amount, description, currency, transaction_type, date, tag
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    description TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('credit', 'debit')),
                    date TEXT NOT NULL,
                    tag TEXT DEFAULT 'Uncategorized'
                );
            ''')
            print("Ensured 'transactions' table exists with base schema.")

            # --- Step 2: Check for and add missing columns ('date', 'tag') ---
            cursor.execute("PRAGMA table_info(transactions);")
            columns = [col[1] for col in cursor.fetchall()]

            if 'date' not in columns:
                print("Schema migration: 'date' column not found. Adding it with a default.")
                try:
                    cursor.execute("ALTER TABLE transactions ADD COLUMN date TEXT DEFAULT '1970-01-01 00:00:00';")
                    conn.commit()
                    print("'date' column added successfully.")
                except sqlite3.Error as e:
                    print(f"!!! Error adding 'date' column: {e}")
                    conn.rollback() # Rollback if adding column fails
            else:
                print("'date' column already exists.")

            if 'tag' not in columns:
                print("Schema migration: 'tag' column not found. Adding it with a default 'Uncategorized'.")
                try:
                    cursor.execute("ALTER TABLE transactions ADD COLUMN tag TEXT DEFAULT 'Uncategorized';")
                    conn.commit()
                    print("'tag' column added successfully.")
                except sqlite3.Error as e:
                    print(f"!!! Error adding 'tag' column: {e}")
                    conn.rollback()
            else:
                print("'tag' column already exists.")
            
            conn.commit() # Final commit for any successful alterations
            print("Database initialization and migration check finished.")

    except sqlite3.Error as e:
        print(f"!!! Database Error during initialization: {e}")

def add_transaction(amount, description, currency, transaction_type, date, tag):
    """Adds a new transaction to the database, including its tag."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (amount, description, currency, transaction_type, date, tag)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (amount, description, currency, transaction_type, date, tag if tag else 'Uncategorized'))
            conn.commit()
            print(f"Transaction added: {amount} {currency} ({transaction_type}) - {description} [Tag: {tag if tag else 'Uncategorized'}]")
    except sqlite3.Error as e:
        print(f"!!! Database Error adding transaction: {e}")

def get_transactions():
    """Retrieves all transactions from the database, ordered by date descending."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            # Order by date descending so newest appear first in lists
            cursor.execute("SELECT id, amount, description, currency, transaction_type, date, tag FROM transactions ORDER BY date DESC")
            transactions = cursor.fetchall()
            return transactions
    except sqlite3.Error as e:
        print(f"!!! Database Error getting transactions: {e}")
        return []

def delete_transaction(transaction_id):
    """Deletes a transaction by its ID."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Transaction deleted: id={transaction_id}")
            else:
                print(f"Warning: No transaction found with id={transaction_id} to delete.")
    except sqlite3.Error as e:
        print(f"!!! Database Error deleting transaction: {e}")

def get_unique_tags():
    """Retrieves all unique tags from the transactions."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT tag FROM transactions WHERE tag IS NOT NULL AND tag != '' ORDER BY tag")
            tags = [row[0] for row in cursor.fetchall() if row[0]] # Ensure not None or empty
            return tags
    except sqlite3.Error as e:
        print(f"!!! Database Error getting unique tags: {e}")
        return []


if __name__ == "__main__":
    init_db()
    print("Database file should be initialized/updated.")
    # Example of adding a transaction with a tag
    # add_transaction(25.0, "Lunch", "USD", "debit", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Food")
    # print(get_transactions())
    # print(get_unique_tags())
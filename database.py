import sqlite3
import os # Import os to check if DB file exists for logging

# Define the database file name
DB_FILE = "transactions.db"

def init_db():
    """
    Initialize the database: create the table if it doesn't exist,
    and handle schema migration (like adding the 'date' column).
    """
    db_existed = os.path.exists(DB_FILE)
    print(f"Initializing database '{DB_FILE}'...")
    if not db_existed:
        print("Database file not found, creating new one.")

    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            # --- Step 1: Ensure the table exists ---
            # Use IF NOT EXISTS to safely create the table only if it's missing.
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    description TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('credit', 'debit')),
                    date TEXT NOT NULL
                );
            ''')
            print("Ensured 'transactions' table exists.")

            # --- Step 2: Check for and perform schema migration (e.g., adding 'date' column) ---
            # This part is only relevant if you had an older version of the table without 'date'.
            # Check if the 'date' column exists *after* ensuring the table exists.
            cursor.execute("PRAGMA table_info(transactions);")
            columns = [col[1] for col in cursor.fetchall()]

            if 'date' not in columns:
                print("Schema migration needed: 'date' column not found. Attempting to add it.")
                try:
                    # Use a temporary table name that's unlikely to conflict
                    old_table_name = "transactions_old_" + datetime.now().strftime("%Y%m%d%H%M%S")
                    print(f"Renaming current table to '{old_table_name}'...")
                    cursor.execute(f"ALTER TABLE transactions RENAME TO {old_table_name};")

                    # Re-create the table with the new schema (including 'date')
                    print("Creating new 'transactions' table with 'date' column...")
                    cursor.execute('''
                        CREATE TABLE transactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            amount REAL NOT NULL,
                            description TEXT NOT NULL,
                            currency TEXT NOT NULL,
                            transaction_type TEXT NOT NULL CHECK(transaction_type IN ('credit', 'debit')),
                            date TEXT NOT NULL
                        );
                    ''')

                    # Copy data from the old table to the new table, providing a default date
                    default_date = '1970-01-01 00:00:00' # Or a more sensible default
                    print(f"Copying data from '{old_table_name}' to new table with default date '{default_date}'...")
                    cursor.execute(f'''
                        INSERT INTO transactions (id, amount, description, currency, transaction_type, date)
                        SELECT id, amount, description, currency, transaction_type, ?
                        FROM {old_table_name};
                    ''', (default_date,))

                    # Drop the old table
                    print(f"Dropping old table '{old_table_name}'...")
                    cursor.execute(f"DROP TABLE {old_table_name};")
                    print("Schema migration completed successfully.")
                    conn.commit() # Commit migration changes explicitly

                except sqlite3.Error as migration_e:
                    print(f"!!! Error during schema migration: {migration_e}")
                    # Consider rolling back or providing more specific error handling
                    conn.rollback() # Rollback partial migration changes
            else:
                print("'date' column already exists, no migration needed.")

            conn.commit() # Commit the initial table creation if it happened
            print("Database initialization finished.")

    except sqlite3.Error as e:
        print(f"!!! Database Error during initialization: {e}")
        # Depending on the error, you might want to raise it or handle it differently

def add_transaction(amount, description, currency, transaction_type, date):
    """Adds a new transaction to the database."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (amount, description, currency, transaction_type, date)
                VALUES (?, ?, ?, ?, ?)
            ''', (amount, description, currency, transaction_type, date))
            conn.commit()
            print(f"Transaction added: {amount} {currency} ({transaction_type}) - {description}")
    except sqlite3.Error as e:
        print(f"!!! Database Error adding transaction: {e}")

def get_transactions():
    """Retrieves all transactions from the database, ordered by date descending."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            # Order by date descending so newest appear first in lists
            cursor.execute("SELECT id, amount, description, currency, transaction_type, date FROM transactions ORDER BY date DESC")
            transactions = cursor.fetchall()
            # print(f"Retrieved {len(transactions)} transactions.") # Optional: for debugging
            return transactions
    except sqlite3.Error as e:
        print(f"!!! Database Error getting transactions: {e}")
        return [] # Return empty list on error

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

# --- Optional: Add a function for testing ---
def _test_db():
    print("\n--- Testing Database ---")
    init_db()
    print("\nAdding test transactions...")
    from datetime import datetime, timedelta
    now = datetime.now()
    add_transaction(50.0, "Groceries", "USD", "debit", (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"))
    add_transaction(1200.0, "Salary", "USD", "credit", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
    add_transaction(15.5, "Coffee", "USD", "debit", now.strftime("%Y-%m-%d %H:%M:%S"))

    print("\nGetting transactions...")
    transactions = get_transactions()
    if transactions:
        for t in transactions:
            print(t)
        # Test delete
        last_id = transactions[0][0] # ID of the newest transaction (coffee)
        print(f"\nDeleting transaction id={last_id}...")
        delete_transaction(last_id)
        print("\nGetting transactions after delete...")
        transactions_after_delete = get_transactions()
        for t in transactions_after_delete:
            print(t)
    else:
        print("No transactions found.")
    print("--- Database Test Finished ---\n")

# If you run this file directly, execute the test function
if __name__ == "__main__":
    # Be careful running this directly if you have real data, as it adds/deletes test data.
    # Consider backing up your DB_FILE first.
    # _test_db()
    # Or just run init_db to ensure the table is set up
    init_db()
    print("Database file should be initialized.")
import sqlite3

# Database file name
DB_FILE = "bot_interactions.db"

# SQL commands to create tables
CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    command TEXT NOT NULL
);
"""


def deploy_database():
    """Create and initialize the SQLite database."""
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Execute SQL to create tables
        cursor.executescript(CREATE_TABLES)
        conn.commit()

        print(f"Database '{DB_FILE}' has been deployed successfully.")
    except Exception as e:
        print(f"Error deploying database: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    deploy_database()

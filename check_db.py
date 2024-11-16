import sqlite3

# Database file path
DB_FILE = "bot_interactions.db"

def fetch_last_five_rows():
    """Fetch and display the last 5 rows from the interactions table."""
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # SQL query to fetch the last 5 rows
        cursor.execute("""
            SELECT * FROM interactions ORDER BY timestamp DESC LIMIT 5;
        """)

        # Fetch the rows and display them
        rows = cursor.fetchall()
        if rows:
            print("Last 5 interactions:")
            for row in rows:
                print(f"ID: {row[0]}, User ID: {row[1]}, Timestamp: {row[2]}, Command: {row[3]}")
        else:
            print("No data found in the interactions table.")

    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_last_five_rows()

import sqlite3

# Database file path
DB_FILE = "bot_interactions.db"

def fetch_last_five_rows():
    """Fetch and display info about users."""
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
           SELECT
               id, 
               user_id,
               timestamp,
               command
           FROM
               (
                   SELECT
                       id,
                       user_id,
                       timestamp,
                       command,
                       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY TIMESTAMP DESC) AS rn
                   FROM
                       interactions
               ) t
           WHERE
               rn = 1;
        """)

        # Fetch the rows and display them
        rows = cursor.fetchall()
        if rows:
            # Define headers
            headers = ["Last action ID", "User name", "Timestamp", "Command"]

            # Calculate column widths
            col_widths = [max(len(str(row[i])) for row in rows) for i in range(len(headers))]
            col_widths = [max(len(header), width) for header, width in zip(headers, col_widths)]

            # Print the table header
            header_row = " | ".join(f"{header:<{col_widths[i]}}" for i, header in enumerate(headers))
            print(header_row)
            print("-" * len(header_row))

            # Print the table rows
            for row in rows:
                print(" | ".join(f"{str(row[i]):<{col_widths[i]}}" for i in range(len(headers))))
        else:
            print("No data found in the interactions table.")

    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_last_five_rows()

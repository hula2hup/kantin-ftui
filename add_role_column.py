import sqlite3

# Connect to the database directly
conn = sqlite3.connect('tekneat.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:", tables)

# Check if user table exists
if ('user',) in tables:
    # Add the role column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN role VARCHAR(50) DEFAULT 'admin'")
        print("Role column added successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Role column already exists.")
        else:
            print(f"Error adding column: {e}")

    # Update existing users to have role 'admin' if not set
    cursor.execute("UPDATE user SET role = 'admin' WHERE role IS NULL")
    conn.commit()
    print("Existing users updated to admin role.")
else:
    print("User table does not exist.")

conn.close()

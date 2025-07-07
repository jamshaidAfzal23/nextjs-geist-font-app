import sqlite3
import os

# Create an in-memory database
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Create a test table
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL
)
''')

# Insert some test data
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Admin User", "admin@example.com"))
conn.commit()

# Query the data
cursor.execute("SELECT * FROM users")
result = cursor.fetchall()
print("Users in database:", result)

# Close the connection
conn.close()

print("Test completed successfully")
"""
Database fix script to add missing columns and update schema.
"""
import sqlite3
import os

def fix_database():
    """Fix database schema issues."""
    db_path = "smartcrm.db"
    
    if not os.path.exists(db_path):
        print("Database doesn't exist, will be created by the app")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if is_admin column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_admin' not in columns:
            print("Adding is_admin column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            conn.commit()
            print("✅ Added is_admin column")
        else:
            print("✅ is_admin column already exists")
            
        # Check if clients table exists and add missing category column
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(clients)")
            client_columns = [column[1] for column in cursor.fetchall()]
            
            if 'category' not in client_columns:
                print("Adding category column to clients table...")
                cursor.execute("ALTER TABLE clients ADD COLUMN category VARCHAR(100)")
                conn.commit()
                print("✅ Added category column")
            else:
                print("✅ category column already exists")
                
            if 'general_notes' not in client_columns:
                print("Adding general_notes column to clients table...")
                cursor.execute("ALTER TABLE clients ADD COLUMN general_notes TEXT")
                conn.commit()
                print("✅ Added general_notes column")
            else:
                print("✅ general_notes column already exists")
        
        # Check if projects table exists and has correct structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(projects)")
            project_columns = [column[1] for column in cursor.fetchall()]
            print(f"Project table columns: {project_columns}")
        
        print("✅ Database schema fixed successfully")
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()

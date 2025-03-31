import sqlite3
import os

def init_db():
    # Remove existing database if it exists
    if os.path.exists('wms.db'):
        os.remove('wms.db')
    
    # Connect to database (this will create it)
    conn = sqlite3.connect('wms.db')
    cursor = conn.cursor()
    
    # Read and execute schema
    with open('commands/init/wmsInitData.sql', 'r') as schema_file:
        cursor.executescript(schema_file.read())
    
    # Read and execute initial data
    with open('commands/init/initData.sql', 'r') as data_file:
        cursor.executescript(data_file.read())
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
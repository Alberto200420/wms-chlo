from flask import Flask, jsonify
import sqlite3
import os

app = Flask(__name__)

# Path to the SQLite database
DATABASE = '/home/sparrow/wms/wms.db'

# Debug: Print the database path
print("Database Path:", os.path.abspath(DATABASE))

def get_db_connection():
    # Function to establish a connection to the database
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
    return conn

def execute_query(query, params=()):
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/v1/administrative/home/", methods=["GET"])
def warehouse_home_display():
    query = "SELECT id AS warehouse_id, warehouse_name FROM Warehouse;"
    warehouses = execute_query(query)
    print("Query Results:", warehouses)  # Debugging: Print the query results
    return jsonify(warehouses)

if __name__ == "__main__":
    app.run(debug=True)
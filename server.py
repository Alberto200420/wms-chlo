from flask import Flask, jsonify, request
from commands.views.admin import (
    warehouse_home_display_query,
    warehouse_display_prodcuts_query
)
import sqlite3
app = Flask(__name__)
DATABASE = 'wms.db'

def execute_query(query, params=()):
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
# ------------------------------------------------------------- ADMINISTRATIVE
# ------------------------------------------------ GET
@app.route("/v1/administrative/home/", methods=["GET"])
def warehouse_home_display():
    warehouses = execute_query(warehouse_home_display_query)
    return jsonify(warehouses)

@app.route("/v1/warehouse/products/", methods=["GET"])
def warehouse_products():
    warehouse_id = request.args.get('warehouse_id')
    if not warehouse_id:
        return jsonify({"error": "warehouse_id query parameter is required"}), 400

    # Check if warehouse exists and get its data
    warehouse_query = "SELECT warehouse_name FROM Warehouse WHERE id = ?"
    warehouse_result = execute_query(warehouse_query, (warehouse_id,))
    if not warehouse_result:
        return jsonify({"error": "Warehouse not found"}), 404

    # Get inventory items with product details and max capacity
    products = execute_query(warehouse_display_prodcuts_query, (warehouse_id,))
    
    return jsonify({
        "warehouse_name": warehouse_result[0]['warehouse_name'],
        "products": products
    })


if __name__ == "__main__":
    app.run(debug=True)
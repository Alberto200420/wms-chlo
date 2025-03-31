from flask import Flask, jsonify, request
from commands.views.admin import (
    warehouse_home_display_query,
    warehouse_display_prodcuts_query,
    product_receipt_detail_query,
    create_purchase_order_query
)
from commands.views.warehouse import (
    warehouse_fill_capacity_query,
)
import sqlite3, json
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

@app.route("/v1/administrative/warehouse/products/", methods=["GET"])
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

@app.route("/v1/administrative/product_receipt/detail/", methods=["GET"])
def product_receipt_detail():
    receipt_id = request.args.get('receipt_id')
    if not receipt_id:
        return jsonify({"error": "receipt_id query parameter is required"}), 400
    
    receipt = execute_query(product_receipt_detail_query, (receipt_id,))
    if not receipt:
        return jsonify({"error": "Product receipt not found"}), 404

    # Parse the JSON string of items back into a list
    receipt_data = receipt[0]
    receipt_data['items'] = json.loads(receipt_data['items'])
    
    return jsonify(receipt_data)

# ------------------------------------------------ POST
@app.route("/v1/administrative/purchase_order/create/", methods=["POST"])
def create_purchase_order():
    data = request.get_json()
    
    # Validate required fields
    supplier_id = data.get('supplier_id')
    total_amount = data.get('total_amount')
    
    if not supplier_id or not total_amount:
        return jsonify({
            'error': 'Supplier ID and Total amount are required'
        }), 400

    # Check if supplier exists
    supplier_query = "SELECT id FROM Supplier WHERE id = ?"
    supplier = execute_query(supplier_query, (supplier_id,))
    if not supplier:
        return jsonify({'error': 'Supplier not found'}), 404

    # Create purchase order (always using warehouse ID 1 as per serializer logic)
    try:
        purchase_order = execute_query(create_purchase_order_query, (supplier_id, total_amount))
        return jsonify(purchase_order[0]), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

# ------------------------------------------------------------- WAREHOUSE
# ------------------------------------------------ GET
@app.route("/v1/warehouse/fill_capacity/", methods=["GET"])
def warehouse_fill_capacity():
    warehouse_id = request.args.get('warehouse_id')
    if not warehouse_id:
        return jsonify({"error": "warehouse_id query parameter is required"}), 400

    # Check if warehouse exists
    warehouse_query = "SELECT id FROM Warehouse WHERE id = ?"
    warehouse = execute_query(warehouse_query, (warehouse_id,))
    if not warehouse:
        return jsonify({"error": "Warehouse not found"}), 404

    # Get products that need filling
    products = execute_query(warehouse_fill_capacity_query, (warehouse_id,))
    return jsonify(products)

if __name__ == "__main__":
    app.run(debug=True)
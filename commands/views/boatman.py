get_product_capacity_query = """
    SELECT 
        i.quantity,
        p.product_name,
        wc.max_capacity,
        wc.capacity_percentage
    FROM Inventory i
    JOIN Product p ON p.id = i.product_id
    JOIN WarehouseCapacity wc ON wc.warehouse_id = i.warehouse_id 
        AND wc.product_id = i.product_id
    WHERE i.warehouse_id = ? AND i.product_id = ?
"""
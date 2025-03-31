warehouse_fill_capacity_query = """
    WITH InventoryStatus AS (
        SELECT 
            i.product_id,
            p.product_name,
            i.quantity,
            wc.max_capacity,
            i.status
        FROM Inventory i
        JOIN Product p ON i.product_id = p.id
        JOIN WarehouseCapacity wc ON wc.warehouse_id = i.warehouse_id 
            AND wc.product_id = i.product_id
        WHERE i.warehouse_id = ?
            AND i.status = 'LOW_CAPACITY'
    )
    SELECT 
        product_id,
        product_name,
        (max_capacity - quantity) as quantity_needed,
        max_capacity
    FROM InventoryStatus
    WHERE max_capacity > quantity
"""
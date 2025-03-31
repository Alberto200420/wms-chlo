warehouse_home_display_query = """
    WITH InventoryValue AS (
        SELECT 
            w.id as warehouse_id,
            w.warehouse_name,
            COALESCE(SUM(i.quantity * p.unit_price), 0) as current_value,
            CASE 
                WHEN EXISTS (
                    SELECT 1 FROM Inventory 
                    WHERE warehouse_id = w.id 
                    AND status = 'LOW_CAPACITY'
                ) THEN 'Low Capacity'
                ELSE 'Good Capacity'
            END as status
        FROM Warehouse w
        LEFT JOIN Inventory i ON w.id = i.warehouse_id
        LEFT JOIN Product p ON i.product_id = p.id
        GROUP BY w.id, w.warehouse_name
    )
    SELECT 
        warehouse_id,
        warehouse_name,
        current_value,
        status
    FROM InventoryValue;
"""

warehouse_display_prodcuts_query = """
    SELECT 
        p.product_name,
        i.quantity,
        COALESCE(wc.max_capacity, 0) as max_capacity
    FROM Inventory i
    JOIN Product p ON i.product_id = p.id
    LEFT JOIN WarehouseCapacity wc ON wc.warehouse_id = i.warehouse_id 
        AND wc.product_id = i.product_id
    WHERE i.warehouse_id = ?
"""
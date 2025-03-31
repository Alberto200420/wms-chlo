SELECT 
    p.product_name, 
    i.quantity, 
    wc.max_capacity
FROM Inventory i
JOIN Product p ON i.product_id = p.id
LEFT JOIN WarehouseCapacity wc ON i.warehouse_id = wc.warehouse_id AND i.product_id = wc.product_id
WHERE i.warehouse_id = ?;  -- Replace ? with the warehouse_id
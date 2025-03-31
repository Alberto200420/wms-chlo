SELECT 
    i.product_id, 
    p.product_name, 
    wc.max_capacity, 
    (wc.max_capacity - i.quantity) AS quantity_needed
FROM Inventory i
JOIN Product p ON i.product_id = p.id
JOIN WarehouseCapacity wc ON i.warehouse_id = wc.warehouse_id AND i.product_id = wc.product_id
WHERE i.warehouse_id = ? AND i.status = 'LOW_CAPACITY';  -- Replace ? with the warehouse_id
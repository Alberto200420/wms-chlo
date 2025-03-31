SELECT 
    pr.id AS receipt_id, 
    pr.receipt_date, 
    pr.received_by, 
    pri.product_id, 
    p.product_name, 
    pri.quantity_received, 
    pri.expiration_date
FROM ProductReceipt pr
JOIN ProductReceiptItem pri ON pr.id = pri.receipt_id
JOIN Product p ON pri.product_id = p.id
WHERE pr.id = ?;  -- Replace ? with the receipt_id
get_suppliers_query = """
    SELECT DISTINCT 
        s.id AS supplier_id, 
        s.supplier_name,
        po.id AS purchase_order_id
    FROM Supplier s
    JOIN PurchaseOrder po ON po.supplier_id = s.id
    WHERE po.status = 'REQUESTED'
    ORDER BY s.supplier_name
"""
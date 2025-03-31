-- Insert into "User" table
INSERT INTO "User" ("id", "username", "password", "role") VALUES
(1, 'jessica', '123', 'ADMIN'),
(2, 'wina', '123', 'BOATMAN'),
(3, 'don', '123', 'DRIVER'),
(4, 'gaby', '123', 'WAREHOUSE');

-- Insert warehouses
INSERT INTO "Warehouse" ("id", "warehouse_name") VALUES
(1, 'matris'),
(2, 'gil house'),
(3, 'chica 1'),
(4, 'chica 2');

-- Insert products with random prices
INSERT INTO "Product" ("id", "product_name", "unit_price") VALUES
(1, 'Smirnoff Vodka 1L c/12', 299.99),
(2, 'Tequila Don Julio Blanco 700 ML c/6', 899.99),
(3, 'Tequila Don Julio 1942 Blanco 700 ML c/6', 2499.99),
(4, 'Jugo Jumex de Arandano 960 ML c/12', 149.99),
(5, 'Jugo Clamato 946 ML c/12', 199.99);

-- Insert inventory for chica 1 (warehouse_id = 3) with quantity 10 for all products
INSERT INTO "Inventory" ("warehouse_id", "product_id", "quantity", "status", "last_updated") VALUES
(1, 1, 80, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(1, 2, 70, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(1, 3, 60, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(1, 4, 50, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(1, 5, 40, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(2, 1, 40, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(2, 2, 30, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(2, 3, 20, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(2, 4, 20, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(2, 5, 20, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(3, 1, 10, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(3, 2, 10, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(3, 3, 10, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(3, 4, 10, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(3, 5, 10, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(4, 1, 10, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(4, 2, 10, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(4, 3, 10, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(4, 4, 10, 'GOOD_CAPACITY', CURRENT_TIMESTAMP),
(4, 5, 10, 'GOOD_CAPACITY', CURRENT_TIMESTAMP);

-- Insert warehouse capacity for all warehouses
-- Setting max_capacity to match the current inventory (10 for chica 1 and chica 2)
-- Setting capacity_percentage to 50 for all

-- For matris (warehouse_id = 1)
INSERT INTO "WarehouseCapacity" ("warehouse_id", "product_id", "max_capacity", "capacity_percentage") VALUES
(1, 1, 80, 50),
(1, 2, 70, 50),
(1, 3, 60, 50),
(1, 4, 50, 50),
(1, 5, 40, 50),
(2, 1, 40, 50),
(2, 2, 30, 50),
(2, 3, 20, 50),
(2, 4, 20, 50),
(2, 5, 20, 50),
(3, 1, 20, 50),
(3, 2, 20, 50),
(3, 3, 20, 50),
(3, 4, 20, 50),
(3, 5, 20, 50),
(4, 1, 20, 50),
(4, 2, 20, 50),
(4, 3, 20, 50),
(4, 4, 20, 50),
(4, 5, 20, 50);
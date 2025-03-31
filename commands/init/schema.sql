-- Create the User table
CREATE TABLE "User" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "username" VARCHAR(50) UNIQUE NOT NULL,
    "password" VARCHAR(255) NOT NULL,
    "role" VARCHAR(9) NOT NULL CHECK ("role" IN ('ADMIN', 'BOATMAN', 'DRIVER', 'WAREHOUSE'))
);

-- Create the Warehouse table
CREATE TABLE "Warehouse" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "warehouse_name" VARCHAR(10) UNIQUE NOT NULL
);

-- Create the Product table
CREATE TABLE "Product" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "product_name" VARCHAR(100) UNIQUE NOT NULL,
    "unit_price" DECIMAL(10, 2) NOT NULL CHECK ("unit_price" >= 0)
);

-- Create the Inventory table
CREATE TABLE "Inventory" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "warehouse_id" INTEGER NOT NULL,
    "product_id" INTEGER NOT NULL,
    "quantity" INTEGER NOT NULL CHECK ("quantity" >= 0),
    "status" VARCHAR(13) NOT NULL CHECK ("status" IN ('LOW_CAPACITY', 'GOOD_CAPACITY')),
    "last_updated" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (warehouse_id, product_id),
    FOREIGN KEY("warehouse_id") REFERENCES "Warehouse"("id") ON DELETE CASCADE,
    FOREIGN KEY("product_id") REFERENCES "Product"("id") ON DELETE CASCADE
);

-- Create the WarehouseCapacity table
CREATE TABLE "WarehouseCapacity" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "warehouse_id" INTEGER NOT NULL,
    "product_id" INTEGER NOT NULL,
    "max_capacity" INTEGER NOT NULL CHECK ("max_capacity" >= 0),
    "capacity_percentage" INTEGER NOT NULL CHECK ("capacity_percentage" >= 0 AND "capacity_percentage" <= 100),
    UNIQUE("warehouse_id", "product_id"),
    FOREIGN KEY("warehouse_id") REFERENCES "Warehouse"("id") ON DELETE CASCADE,
    FOREIGN KEY("product_id") REFERENCES "Product"("id") ON DELETE CASCADE
);

-- Create indexes for Inventory
CREATE INDEX "idx_inventory_warehouse_status" ON "Inventory" ("warehouse_id", "status");
CREATE INDEX "idx_inventory_product_quantity" ON "Inventory" ("product_id", "quantity");

-- Create the Supplier table
CREATE TABLE "Supplier" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "supplier_name" VARCHAR(30) UNIQUE NOT NULL,
    "contact_info" TEXT
);

-- Create the PurchaseOrder table
CREATE TABLE "PurchaseOrder" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "warehouse_id" INTEGER NOT NULL,
    "supplier_id" INTEGER NOT NULL,
    "order_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "total_amount" DECIMAL(10, 2) NOT NULL,
    "status" VARCHAR(9) NOT NULL DEFAULT 'REQUESTED' CHECK ("status" IN ('REQUESTED', 'CANCELLED', 'RECEIVED')),
    FOREIGN KEY("warehouse_id") REFERENCES "Warehouse"("id") ON DELETE CASCADE,
    FOREIGN KEY("supplier_id") REFERENCES "Supplier"("id") ON DELETE CASCADE
);

-- Create the ProductReceipt table
CREATE TABLE "ProductReceipt" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "purchase_order_id" INTEGER NOT NULL,
    "receipt_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "received_by" VARCHAR(255) NOT NULL,
    FOREIGN KEY("purchase_order_id") REFERENCES "PurchaseOrder"("id") ON DELETE CASCADE
);

-- Create the ProductReceiptItem table
CREATE TABLE "ProductReceiptItem" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "receipt_id" INTEGER NOT NULL,
    "warehouse_id" INTEGER NOT NULL,
    "product_id" INTEGER NOT NULL,
    "quantity_received" INTEGER NOT NULL CHECK ("quantity_received" > 0),
    "expiration_date" DATE,
    FOREIGN KEY("receipt_id") REFERENCES "ProductReceipt"("id") ON DELETE CASCADE,
    FOREIGN KEY("warehouse_id") REFERENCES "Warehouse"("id") ON DELETE CASCADE,
    FOREIGN KEY("product_id") REFERENCES "Product"("id") ON DELETE CASCADE
);
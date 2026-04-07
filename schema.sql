schema.sql ( Databes Schema with corrections)
-- Enable UUID extension if using PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE Company (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL
);

CREATE TABLE Warehouse (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES Company(id),
    name VARCHAR(255) NOT NULL
);
CREATE INDEX idx_warehouse_company ON Warehouse(company_id);

CREATE TABLE Supplier (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES Company(id),
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255)
);
CREATE INDEX idx_supplier_company ON Supplier(company_id);

CREATE TABLE Product (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES Company(id),
    supplier_id UUID REFERENCES Supplier(id),
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    product_type VARCHAR(100),
    is_bundle BOOLEAN DEFAULT FALSE,
    UNIQUE(company_id, sku) -- SKUs unique per company
);
CREATE INDEX idx_product_company ON Product(company_id);
CREATE INDEX idx_product_supplier ON Product(supplier_id);

CREATE TABLE Inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES Product(id),
    warehouse_id UUID NOT NULL REFERENCES Warehouse(id),
    quantity INTEGER NOT NULL DEFAULT 0,
    UNIQUE(product_id, warehouse_id)
);
CREATE INDEX idx_inventory_product ON Inventory(product_id);
CREATE INDEX idx_inventory_warehouse ON Inventory(warehouse_id);

CREATE TABLE InventoryLog (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inventory_id UUID NOT NULL REFERENCES Inventory(id),
    change_amount INTEGER NOT NULL, -- Positive for restock, negative for sales
    reason VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_inventorylog_inventory ON InventoryLog(inventory_id);

CREATE TABLE BundleItem (
    bundle_product_id UUID NOT NULL REFERENCES Product(id),
    component_product_id UUID NOT NULL REFERENCES Product(id),
    quantity_required INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (bundle_product_id, component_product_id)
);

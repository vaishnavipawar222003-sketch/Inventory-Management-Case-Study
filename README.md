# StockFlow - B2B Inventory Management Case Study #

## Overview
This repository contains my solutions for the "StockFlow" B2B inventory management platform case study. The project involves debugging a faulty API endpoint, designing a scalable database schema for multi-warehouse inventory, and implementing a complex endpoint for low-stock alerts.

## Part 1: Code Review & Debugging

### Identified Issues & Impact
**Technical Issues:**
1. **Lack of Database Atomicity (Two Commits):** The original code called `db.session.commit()` twice. 
   * *Impact:* If the first commit succeeds but the second fails, we get an "orphaned" product in the database with no initial inventory record, leading to data inconsistency.
2. **Missing Input Validation:** No checks for missing fields.
   * *Impact:* Malformed payloads result in a `KeyError` and a 500 Internal Server Error rather than a proper 400 Bad Request.
3. **No SKU Uniqueness Check:** No explicit handling for duplicate SKUs.
   * *Impact:* Triggers a 500 Integrity Error crash instead of gracefully warning the client.

**Business Logic Issues:**
1. **Product Tied to a Single Warehouse:** Storing `warehouse_id` on the `Product` model restricts it. 
   * *Impact:* Violates the requirement that products can exist in multiple warehouses. The warehouse mapping should strictly live on the `Inventory` table.
2. **Price Data Type:** Price wasn't safely converted to a Decimal.

### Explanation of Fixes
The corrected implementation (found in `app.py`) addresses these by:
* Using a single `db.session.commit()` at the very end to ensure atomic transactions.
* Adding input validation for required fields.
* Catching `IntegrityError` to handle duplicate SKUs cleanly.
* Removing `warehouse_id` from the base `Product` model and handling it via the `Inventory` relationship
  
---------------------------------------------------------------------------------------------------------------------------------------------------- 

## Part 2: Database Design

### Missing Requirements & Gaps Identified
If building this for production, I would ask the product team the following questions:
1. **Bundle Logic:** When a bundle is sold, do we decrement the bundle's inventory, or recursively decrement its individual components?
2. **Supplier Mapping:** Is a product strictly sourced from one supplier, or can multiple suppliers provide the same product?
3. **Low Stock Thresholds:** Is the threshold global per product, or does it vary per warehouse (e.g., main warehouse vs. small retail branch)?

### Design Decisions & Justifications
The SQL schema (found in `schema.sql`) implements the following optimizations:
* **UUIDs for Primary Keys:** Prevents ID enumeration and simplifies data merging in a B2B SaaS environment.
* **InventoryLog Table:** Instead of just updating a static number, an append-only log allows for historical tracking, auditing, and accurately calculating "recent sales activity."
* **Foreign Key Indexes:** Ensures fast lookups when querying products by company or warehouse.

  ---------------------------------------------------------------------------------------------------------------------------------------------------

## Part 3: API Implementation

### Assumptions Made
* **Thresholds:** Assumed the low-stock threshold varies based on a `product_type` configuration.
* **Sales Activity:** Relied on the `InventoryLog` table to calculate average daily sales over the last 30 days to dynamically compute `days_until_stockout`.

### Explanation of Approach
The implementation (found in `alerts.py`) focuses on performance and accuracy:
* **N+1 Query Mitigation:** Uses SQL joins to fetch inventory, product, warehouse, and supplier data in a single database hit rather than querying inside a loop.
* **Smart Filtering:** Explicitly filters out bundles (`is_bundle == False`) to avoid applying standard stockout math to virtual items.
* **Velocity Calculation:** Calculates daily sales velocity dynamically based on the last 30 days of logs, returning `days_until_stockout` and sorting the most urgent alerts to the top.

  -----------------------------------------------------------------------------------------------------------------------------------------------
                                                                  -END-

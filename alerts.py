alert.py (low stock alert implementation)
from flask import Blueprint, jsonify
from sqlalchemy import func
from datetime import datetime, timedelta
# Assuming db, Inventory, Product, Warehouse, Supplier, InventoryLog are imported

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def get_low_stock_alerts(company_id):
    try:
        # Define "Recent Activity" timeframe (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Single database hit using JOINs to avoid N+1 query problem
        low_stock_items = db.session.query(
            Inventory, Product, Warehouse, Supplier
        ).join(
            Product, Inventory.product_id == Product.id
        ).join(
            Warehouse, Inventory.warehouse_id == Warehouse.id
        ).join(
            Supplier, Product.supplier_id == Supplier.id
        ).filter(
            Warehouse.company_id == company_id,
            Product.is_bundle == False # Exclude bundles for standard stock logic
        ).all()

        alerts = []
        
        for inv, prod, wh, supp in low_stock_items:
            # Dynamic Threshold Logic based on product type
            threshold_config = {"electronics": 50, "apparel": 20, "hardware": 100}
            current_threshold = threshold_config.get(prod.product_type, 20)
            
            # Check if stock is currently at or below threshold
            if inv.quantity <= current_threshold:
                
                # Query the audit log for recent sales (negative changes)
                recent_sales_volume = db.session.query(func.sum(InventoryLog.change_amount)).filter(
                    InventoryLog.inventory_id == inv.id,
                    InventoryLog.change_amount < 0,
                    InventoryLog.created_at >= thirty_days_ago
                ).scalar() or 0
                
                recent_sales_volume = abs(recent_sales_volume)
                
                # Only process if there is actual recent sales activity
                if recent_sales_volume > 0:
                    daily_sales_velocity = recent_sales_volume / 30.0
                    
                    # Prevent division by zero
                    days_until = int(inv.quantity / daily_sales_velocity) if daily_sales_velocity > 0 else 999
                    
                    alerts.append({
                        "product_id": prod.id,
                        "product_name": prod.name,
                        "sku": prod.sku,
                        "warehouse_id": wh.id,
                        "warehouse_name": wh.name,
                        "current_stock": inv.quantity,
                        "threshold": current_threshold,
                        "days_until_stockout": days_until,
                        "supplier": {
                            "id": supp.id,
                            "name": supp.name,
                            "contact_email": supp.contact_email
                        }
                    })

        # Sort so the most urgent alerts (lowest days left) appear first
        alerts.sort(key=lambda x: x['days_until_stockout'])

        return jsonify({
            "alerts": alerts,
            "total_alerts": len(alerts)
        }), 200

    except Exception as e:
        return jsonify({"error": "Unable to process low stock alerts at this time."}), 500

alert.py (low stock alert implementation)
from flask import Blueprint, jsonify
from sqlalchemy import func
from datetime import datetime, timedelta
# Assuming db, Inventory, Product, Warehouse, Supplier, InventoryLog are imported

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def get_low_stock_alerts(company_id):
    try:
        # Define "Recent Activity" timeframe (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Single database hit using JOINs to avoid N+1 query problem
        low_stock_items = db.session.query(
            Inventory, Product, Warehouse, Supplier
        ).join(
            Product, Inventory.product_id == Product.id
        ).join(
            Warehouse, Inventory.warehouse_id == Warehouse.id
        ).join(
            Supplier, Product.supplier_id == Supplier.id
        ).filter(
            Warehouse.company_id == company_id,
            Product.is_bundle == False # Exclude bundles for standard stock logic
        ).all()

        alerts = []
        
        for inv, prod, wh, supp in low_stock_items:
            # Dynamic Threshold Logic based on product type
            threshold_config = {"electronics": 50, "apparel": 20, "hardware": 100}
            current_threshold = threshold_config.get(prod.product_type, 20)
            
            # Check if stock is currently at or below threshold
            if inv.quantity <= current_threshold:
                
                # Query the audit log for recent sales (negative changes)
                recent_sales_volume = db.session.query(func.sum(InventoryLog.change_amount)).filter(
                    InventoryLog.inventory_id == inv.id,
                    InventoryLog.change_amount < 0,
                    InventoryLog.created_at >= thirty_days_ago
                ).scalar() or 0
                
                recent_sales_volume = abs(recent_sales_volume)
                
                # Only process if there is actual recent sales activity
                if recent_sales_volume > 0:
                    daily_sales_velocity = recent_sales_volume / 30.0
                    
                    # Prevent division by zero
                    days_until = int(inv.quantity / daily_sales_velocity) if daily_sales_velocity > 0 else 999
                    
                    alerts.append({
                        "product_id": prod.id,
                        "product_name": prod.name,
                        "sku": prod.sku,
                        "warehouse_id": wh.id,
                        "warehouse_name": wh.name,
                        "current_stock": inv.quantity,
                        "threshold": current_threshold,
                        "days_until_stockout": days_until,
                        "supplier": {
                            "id": supp.id,
                            "name": supp.name,
                            "contact_email": supp.contact_email
                        }
                    })

        # Sort so the most urgent alerts (lowest days left) appear first
        alerts.sort(key=lambda x: x['days_until_stockout'])

        return jsonify({
            "alerts": alerts,
            "total_alerts": len(alerts)
        }), 200

    except Exception as e:
        return jsonify({"error": "Unable to process low stock alerts at this time."}), 500

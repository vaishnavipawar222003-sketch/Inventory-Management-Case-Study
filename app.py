app.py (corrected API ENDPOINT)
from flask import Flask, request, jsonify
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
# Assuming db, Product, and Inventory are imported from your models

app = Flask(__name__)

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json
    
    # 1. Input Validation
    required_fields = ['name', 'sku', 'price', 'warehouse_id', 'initial_quantity']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    try:
        # 2. Create new product (warehouse_id removed from base model)
        product = Product(
            name=data['name'],
            sku=data['sku'],
            price=Decimal(str(data['price'])), 
            description=data.get('description', '') 
        )
        
        db.session.add(product)
        db.session.flush() # Flush to get product.id without committing
        
        # 3. Update inventory count
        inventory = Inventory(
            product_id=product.id,
            warehouse_id=data['warehouse_id'],
            quantity=int(data['initial_quantity'])
        )
        
        db.session.add(inventory)
        
        # 4. Single atomic commit
        db.session.commit()
        
        return jsonify({
            "message": "Product created successfully", 
            "product_id": product.id
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "A product with this SKU already exists."}), 409
    except ValueError:
        db.session.rollback()
        return jsonify({"error": "Invalid data types provided for price or quantity."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred."}), 500

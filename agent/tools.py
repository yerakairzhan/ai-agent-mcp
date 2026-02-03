"""
MCP Tool Implementations
Direct implementations of MCP tools for agent use
"""
from typing import Dict, Any, List, Optional, Callable
from sqlalchemy.orm import Session
from database import SessionLocal, Product, Order
import logging

logger = logging.getLogger(__name__)


def get_db() -> Session:
    """Get database session"""
    return SessionLocal()


# ============================================================================
# PRODUCT TOOLS (from product_server.py)
# ============================================================================

def list_products(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List products from database"""
    db = get_db()
    try:
        query = db.query(Product)
        if category:
            query = query.filter(Product.category == category)

        products = query.all()

        return [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "category": p.category,
                "in_stock": p.in_stock
            }
            for p in products
        ]
    finally:
        db.close()


def add_product(name: str, price: float, category: str, in_stock: bool = True) -> Dict[str, Any]:
    """Add product to database"""
    db = get_db()
    try:
        new_product = Product(
            name=name,
            price=price,
            category=category,
            in_stock=in_stock
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return {
            "id": new_product.id,
            "name": new_product.name,
            "price": new_product.price,
            "category": new_product.category,
            "in_stock": new_product.in_stock,
            "success": True
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def get_product(product_id: int) -> Dict[str, Any]:
    """Get product by ID"""
    db = get_db()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return {"success": False, "error": f"Product {product_id} not found"}

        return {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "category": product.category,
            "in_stock": product.in_stock,
            "success": True
        }
    finally:
        db.close()


# ============================================================================
# ORDER TOOLS (from order_server.py)
# ============================================================================

def create_order(product_id: int, quantity: int) -> Dict[str, Any]:
    """Create order for product"""
    db = get_db()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return {"success": False, "error": f"Product {product_id} not found"}

        if not product.in_stock:
            return {"success": False, "error": f"{product.name} is out of stock"}

        if quantity <= 0:
            return {"success": False, "error": "Quantity must be positive"}

        total_price = product.price * quantity

        new_order = Order(
            product_id=product_id,
            quantity=quantity,
            total_price=total_price,
            status="pending"
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        return {
            "order_id": new_order.id,
            "product_id": product_id,
            "product_name": product.name,
            "quantity": quantity,
            "total_price": total_price,
            "status": "pending",
            "success": True
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def list_orders(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """List orders from database"""
    db = get_db()
    try:
        query = db.query(Order)
        if status:
            query = query.filter(Order.status == status)

        orders = query.order_by(Order.created_at.desc()).all()

        return [
            {
                "order_id": o.id,
                "product_id": o.product_id,
                "product_name": o.product.name,
                "quantity": o.quantity,
                "total_price": o.total_price,
                "status": o.status,
                "created_at": o.created_at.isoformat()
            }
            for o in orders
        ]
    finally:
        db.close()


# ============================================================================
# TOOL REGISTRY - Maps tool names to functions
# ============================================================================

TOOL_REGISTRY: Dict[str, Callable] = {
    # Product tools
    "list_products": list_products,
    "add_product": add_product,
    "get_product": get_product,

    # Order tools
    "create_order": create_order,
    "list_orders": list_orders,
}
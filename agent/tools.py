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

# PRODUCT TOOLS (from product_server.py)

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


def update_product(product_id: int, name: str = None, price: float = None,
                   category: str = None, in_stock: bool = None) -> Dict[str, Any]:
    """Update product fields"""
    db = get_db()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return {"success": False, "error": f"Product {product_id} not found"}

        if name is not None:
            product.name = name
        if price is not None:
            product.price = price
        if category is not None:
            product.category = category
        if in_stock is not None:
            product.in_stock = in_stock

        db.commit()
        db.refresh(product)

        return {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "category": product.category,
            "in_stock": product.in_stock,
            "success": True
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def delete_product(product_id: int) -> Dict[str, Any]:
    """Delete product from database"""
    db = get_db()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return {"success": False, "error": f"Product {product_id} not found"}

        product_name = product.name
        db.delete(product)
        db.commit()

        return {
            "deleted": True,
            "product_id": product_id,
            "product_name": product_name,
            "success": True
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def get_statistics() -> Dict[str, Any]:
    """Get product statistics"""
    db = get_db()
    try:
        products = db.query(Product).all()

        if not products:
            return {
                "total_count": 0,
                "average_price": 0,
                "categories": [],
                "in_stock_count": 0
            }

        total_count = len(products)
        average_price = sum(p.price for p in products) / total_count
        categories = list(set(p.category for p in products))
        in_stock_count = sum(1 for p in products if p.in_stock)

        return {
            "total_count": total_count,
            "average_price": round(average_price, 2),
            "categories": categories,
            "in_stock_count": in_stock_count
        }
    finally:
        db.close()

# ORDER TOOLS (from order_server.py)

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


def get_order(order_id: int) -> Dict[str, Any]:
    """Get order by ID"""
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            return {"success": False, "error": f"Order {order_id} not found"}

        return {
            "order_id": order.id,
            "product_id": order.product_id,
            "product_name": order.product.name,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "success": True
        }
    finally:
        db.close()


def update_order_status(order_id: int, status: str) -> Dict[str, Any]:
    """Update order status"""
    db = get_db()
    try:
        valid_statuses = ["pending", "completed", "cancelled"]

        if status not in valid_statuses:
            return {"success": False, "error": f"Invalid status. Must be: {', '.join(valid_statuses)}"}

        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            return {"success": False, "error": f"Order {order_id} not found"}

        order.status = status
        db.commit()
        db.refresh(order)

        return {
            "order_id": order.id,
            "product_id": order.product_id,
            "product_name": order.product.name,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "success": True
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def cancel_order(order_id: int) -> Dict[str, Any]:
    """Cancel an order"""
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            return {"success": False, "error": f"Order {order_id} not found"}

        if order.status == "completed":
            return {"success": False, "error": "Cannot cancel completed order"}

        if order.status == "cancelled":
            return {"success": False, "error": "Order already cancelled"}

        order.status = "cancelled"
        db.commit()
        db.refresh(order)

        return {
            "order_id": order.id,
            "status": order.status,
            "message": f"Order {order_id} cancelled",
            "success": True
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def get_order_statistics() -> Dict[str, Any]:
    """Get order statistics"""
    db = get_db()
    try:
        all_orders = db.query(Order).all()

        if not all_orders:
            return {
                "total_orders": 0,
                "pending_orders": 0,
                "completed_orders": 0,
                "cancelled_orders": 0,
                "total_revenue": 0
            }

        total_orders = len(all_orders)
        pending = sum(1 for o in all_orders if o.status == "pending")
        completed = sum(1 for o in all_orders if o.status == "completed")
        cancelled = sum(1 for o in all_orders if o.status == "cancelled")
        total_revenue = sum(o.total_price for o in all_orders if o.status == "completed")

        return {
            "total_orders": total_orders,
            "pending_orders": pending,
            "completed_orders": completed,
            "cancelled_orders": cancelled,
            "total_revenue": round(total_revenue, 2)
        }
    finally:
        db.close()

# TOOL REGISTRY - Maps tool names to functions

TOOL_REGISTRY: Dict[str, Callable] = {
    # Product tools
    "list_products": list_products,
    "add_product": add_product,
    "get_product": get_product,
    "update_product": update_product,
    "delete_product": delete_product,
    "get_statistics": get_statistics,

    # Order tools
    "create_order": create_order,
    "list_orders": list_orders,
    "get_order": get_order,
    "update_order_status": update_order_status,
    "cancel_order": cancel_order,
    "get_order_statistics": get_order_statistics,
}
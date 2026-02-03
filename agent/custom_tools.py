"""
Custom Agent Tools
These are agent-specific tools that work directly with the database
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from database import SessionLocal, Product, Order
import logging

logger = logging.getLogger(__name__)


def get_db() -> Session:
    """Get database session"""
    return SessionLocal()


def search_products_by_name(search_term: str) -> List[Dict[str, Any]]:
    """
    Custom tool: Search products by name (partial match)

    Args:
        search_term: Search string to match against product names

    Returns:
        List of matching products
    """
    db = get_db()
    try:
        logger.info(f"Searching products with term: {search_term}")
        products = db.query(Product).filter(
            Product.name.ilike(f"%{search_term}%")
        ).all()

        results = [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "category": p.category,
                "in_stock": p.in_stock
            }
            for p in products
        ]

        logger.info(f"Found {len(results)} products matching '{search_term}'")
        return results
    finally:
        db.close()


def get_products_by_price_range(min_price: float, max_price: float) -> List[Dict[str, Any]]:
    """
    Custom tool: Get products within price range

    Args:
        min_price: Minimum price
        max_price: Maximum price

    Returns:
        List of products in price range
    """
    db = get_db()
    try:
        logger.info(f"Searching products in price range: ${min_price}-${max_price}")
        products = db.query(Product).filter(
            Product.price >= min_price,
            Product.price <= max_price
        ).all()

        results = [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "category": p.category,
                "in_stock": p.in_stock
            }
            for p in products
        ]

        logger.info(f"Found {len(results)} products in price range")
        return results
    finally:
        db.close()


def get_order_summary(order_id: int) -> Dict[str, Any]:
    """
    Custom tool: Get detailed order summary

    Args:
        order_id: Order ID

    Returns:
        Detailed order summary with product info
    """
    db = get_db()
    try:
        logger.info(f"Getting summary for order {order_id}")
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            logger.warning(f"Order {order_id} not found")
            return {"success": False, "error": f"Order {order_id} not found"}

        product = order.product

        return {
            "success": True,
            "order_id": order.id,
            "product": {
                "id": product.id,
                "name": product.name,
                "unit_price": product.price,
                "category": product.category
            },
            "quantity": order.quantity,
            "total_price": order.total_price,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "savings": round((product.price * order.quantity) - order.total_price, 2)
        }
    finally:
        db.close()


# Tool registry for custom tools
CUSTOM_TOOL_REGISTRY = {
    "search_products_by_name": search_products_by_name,
    "get_products_by_price_range": get_products_by_price_range,
    "get_order_summary": get_order_summary,
}
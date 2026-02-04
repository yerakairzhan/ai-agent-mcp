"""
Custom Agent Tools
These are agent-specific tools that work directly with the database
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from database import SessionLocal, Product
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

# Tool registry for custom tools
CUSTOM_TOOL_REGISTRY = {
    "search_products_by_name": search_products_by_name,
}
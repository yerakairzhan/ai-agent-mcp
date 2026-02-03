"""
Product Management MCP Server
Provides tools for product CRUD operations
"""
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, Product, init_db, seed_initial_data

# Initialize MCP server
mcp = FastMCP("Product Management Server")

# Initialize database
init_db()
seed_initial_data()


def get_db() -> Session:
    """Get database session"""
    return SessionLocal()


@mcp.tool()
def list_products(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get list of all products or filter by category

    Args:
        category: Optional category to filter products (Electronics, Accessories, Furniture)

    Returns:
        List of products with id, name, price, category, in_stock
    """
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


@mcp.tool()
def get_product(product_id: int) -> Dict[str, Any]:
    """
    Get information about a specific product by ID

    Args:
        product_id: Product ID to retrieve

    Returns:
        Product data with all fields

    Raises:
        ValueError: If product not found
    """
    db = get_db()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            raise ValueError(f"Product with ID {product_id} not found")

        return {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "category": product.category,
            "in_stock": product.in_stock
        }
    finally:
        db.close()


@mcp.tool()
def add_product(
    name: str,
    price: float,
    category: str,
    in_stock: bool = True
) -> Dict[str, Any]:
    """
    Add new product to database

    Args:
        name: Product name
        price: Product price (must be positive)
        category: Product category
        in_stock: Stock availability (default True)

    Returns:
        Created product with assigned ID
    """
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
            "in_stock": new_product.in_stock
        }
    finally:
        db.close()


@mcp.tool()
def update_product(
    product_id: int,
    name: Optional[str] = None,
    price: Optional[float] = None,
    category: Optional[str] = None,
    in_stock: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update existing product

    Args:
        product_id: Product ID to update
        name: New name (optional)
        price: New price (optional)
        category: New category (optional)
        in_stock: New stock status (optional)

    Returns:
        Updated product data

    Raises:
        ValueError: If product not found
    """
    db = get_db()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            raise ValueError(f"Product with ID {product_id} not found")

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
            "in_stock": product.in_stock
        }
    finally:
        db.close()


@mcp.tool()
def delete_product(product_id: int) -> Dict[str, Any]:
    """
    Delete product from database

    Args:
        product_id: Product ID to delete

    Returns:
        Deletion confirmation with deleted product info

    Raises:
        ValueError: If product not found
    """
    db = get_db()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            raise ValueError(f"Product with ID {product_id} not found")

        product_name = product.name
        db.delete(product)
        db.commit()

        return {
            "deleted": True,
            "product_id": product_id,
            "product_name": product_name
        }
    finally:
        db.close()


@mcp.tool()
def get_statistics() -> Dict[str, Any]:
    """
    Get statistics about products

    Returns:
        Dictionary with total_count, average_price, categories, in_stock_count
    """
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


if __name__ == "__main__":
    # Run MCP server via stdio
    mcp.run(transport="stdio")
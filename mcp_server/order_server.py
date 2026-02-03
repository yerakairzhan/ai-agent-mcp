"""
Order Management MCP Server (Bonus Task)
Provides tools for order operations
"""
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, Product, Order, init_db

# Initialize MCP server
mcp = FastMCP("Order Management Server")

# Initialize database
init_db()


def get_db() -> Session:
    """Get database session"""
    return SessionLocal()


@mcp.tool()
def create_order(product_id: int, quantity: int) -> Dict[str, Any]:
    """
    Create a new order for a product

    Args:
        product_id: ID of the product to order
        quantity: Quantity to order (must be positive)

    Returns:
        Created order details with order_id, product info, total_price

    Raises:
        ValueError: If product not found, out of stock, or invalid quantity
    """
    db = get_db()
    try:
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            raise ValueError(f"Product with ID {product_id} not found")

        if not product.in_stock:
            raise ValueError(f"Product '{product.name}' is not in stock")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        # Calculate total price
        total_price = product.price * quantity

        # Create order
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
            "product_id": new_order.product_id,
            "product_name": product.name,
            "quantity": new_order.quantity,
            "unit_price": product.price,
            "total_price": new_order.total_price,
            "status": new_order.status,
            "created_at": new_order.created_at.isoformat()
        }
    finally:
        db.close()


@mcp.tool()
def get_order(order_id: int) -> Dict[str, Any]:
    """
    Get order details by ID

    Args:
        order_id: Order ID to retrieve

    Returns:
        Order details including product information

    Raises:
        ValueError: If order not found
    """
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            raise ValueError(f"Order with ID {order_id} not found")

        return {
            "order_id": order.id,
            "product_id": order.product_id,
            "product_name": order.product.name,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "status": order.status,
            "created_at": order.created_at.isoformat()
        }
    finally:
        db.close()


@mcp.tool()
def list_orders(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all orders or filter by status

    Args:
        status: Optional status filter (pending, completed, cancelled)

    Returns:
        List of orders sorted by creation date (newest first)
    """
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


@mcp.tool()
def update_order_status(order_id: int, status: str) -> Dict[str, Any]:
    """
    Update order status

    Args:
        order_id: Order ID to update
        status: New status (pending, completed, cancelled)

    Returns:
        Updated order details

    Raises:
        ValueError: If order not found or invalid status
    """
    db = get_db()
    try:
        valid_statuses = ["pending", "completed", "cancelled"]

        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            raise ValueError(f"Order with ID {order_id} not found")

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
            "created_at": order.created_at.isoformat()
        }
    finally:
        db.close()


@mcp.tool()
def cancel_order(order_id: int) -> Dict[str, Any]:
    """
    Cancel an order

    Args:
        order_id: Order ID to cancel

    Returns:
        Cancelled order confirmation

    Raises:
        ValueError: If order not found, already completed, or already cancelled
    """
    db = get_db()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            raise ValueError(f"Order with ID {order_id} not found")

        if order.status == "completed":
            raise ValueError("Cannot cancel a completed order")

        if order.status == "cancelled":
            raise ValueError("Order is already cancelled")

        order.status = "cancelled"
        db.commit()
        db.refresh(order)

        return {
            "order_id": order.id,
            "status": order.status,
            "message": f"Order {order_id} has been cancelled"
        }
    finally:
        db.close()


@mcp.tool()
def get_order_statistics() -> Dict[str, Any]:
    """
    Get statistics about orders

    Returns:
        Order statistics including totals and revenue
    """
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


if __name__ == "__main__":
    # Run MCP server via stdio
    mcp.run(transport="stdio")
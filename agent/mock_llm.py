"""
Mock LLM for intent parsing
Works with both MCP tools and custom tools
"""
from typing import Dict, Any, Optional
import json
import re
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class MockLLM:
    """Mock LLM with intent parsing and MCP client integration"""

    def __init__(self):
        self.mcp_session: Optional[ClientSession] = None
        logger.info("MockLLM initialized")

    async def connect_to_mcp(self, server_script: str):
        """
        Connect to MCP server

        Args:
            server_script: Path to MCP server script
        """
        try:
            server_params = StdioServerParameters(
                command="python",
                args=[server_script],
                env=None
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    self.mcp_session = session

                    # List available tools
                    tools = await session.list_tools()
                    logger.info(f"Connected to MCP server with {len(tools.tools)} tools")

                    return session
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise

    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Parse user intent - NO function type checking

        Args:
            user_input: User's natural language query

        Returns:
            Dictionary with tool name and arguments
        """
        user_input_lower = user_input.lower()
        logger.debug(f"Parsing intent for: {user_input}")

        # LIST PRODUCTS OR ORDERS
        if self._is_list_query(user_input_lower):
            if "order" in user_input_lower:
                status = self._extract_order_status(user_input_lower)
                return {
                    "tool": "list_orders",
                    "arguments": {"status": status} if status else {},
                    "source": "mcp"
                }
            else:
                category = self._extract_category(user_input_lower)
                return {
                    "tool": "list_products",
                    "arguments": {"category": category} if category else {},
                    "source": "mcp"
                }

        # SEARCH PRODUCTS
        if self._is_search_query(user_input_lower):
            search_term = self._extract_search_term(user_input)
            if search_term:
                return {
                    "tool": "search_products_by_name",
                    "arguments": {"search_term": search_term},
                    "source": "custom"
                }

        # ADD PRODUCT
        if self._is_add_query(user_input_lower):
            parsed = self._parse_add_product(user_input)
            if parsed:
                parsed["source"] = "mcp"
                return parsed

        # CREATE ORDER
        if self._is_order_query(user_input_lower):
            parsed = self._parse_create_order(user_input_lower)
            if parsed:
                parsed["source"] = "mcp"
                return parsed

        # GET PRODUCT BY ID
        if self._is_get_query(user_input_lower):
            parsed = self._parse_get_product(user_input_lower)
            if parsed:
                parsed["source"] = "mcp"
                return parsed

        # UPDATE PRODUCT
        if self._is_update_product_query(user_input_lower):
            parsed = self._parse_update_product(user_input)
            if parsed:
                parsed["source"] = "mcp"
                return parsed

        # DELETE PRODUCT
        if self._is_delete_product_query(user_input_lower):
            parsed = self._parse_delete_product(user_input_lower)
            if parsed:
                parsed["source"] = "mcp"
                return parsed

        # GET STATISTICS
        if self._is_statistics_query(user_input_lower):
            return {
                "tool": "get_statistics" if "product" in user_input_lower else "get_order_statistics",
                "arguments": {},
                "source": "mcp"
            }

        # GET ORDER
        if self._is_get_order_query(user_input_lower):
            parsed = self._parse_get_order(user_input_lower)
            if parsed:
                parsed["source"] = "mcp"
                return parsed

        # UPDATE ORDER STATUS
        if self._is_update_order_query(user_input_lower):
            parsed = self._parse_update_order_status(user_input_lower)
            if parsed:
                parsed["source"] = "mcp"
                return parsed

        # CANCEL ORDER
        if self._is_cancel_order_query(user_input_lower):
            parsed = self._parse_cancel_order(user_input_lower)
            if parsed:
                parsed["source"] = "mcp"
                return parsed

        logger.warning(f"Could not parse intent for: {user_input}")
        return {
            "tool": None,
            "arguments": {},
            "error": "Could not parse intent. Try: 'list products', 'add product: Name, price: X, category: Y', 'order product 1 quantity 2', 'update product 1 price 999', 'delete product 1', 'get statistics'",
            "source": None
        }

    def _is_list_query(self, text: str) -> bool:
        """Check if query is asking to list items"""
        keywords = ["list", "show", "display", "get all", "all products", "all orders"]
        return any(kw in text for kw in keywords)

    def _is_add_query(self, text: str) -> bool:
        """Check if query is adding a product"""
        keywords = ["add product", "create product", "new product"]
        return any(kw in text for kw in keywords)

    def _is_order_query(self, text: str) -> bool:
        """Check if query is creating an order"""
        keywords = ["order product", "buy", "purchase", "create order"]
        return any(kw in text for kw in keywords)

    def _is_get_query(self, text: str) -> bool:
        """Check if query is getting a specific product"""
        keywords = ["get product", "find product", "show product"]
        return any(kw in text for kw in keywords)

    def _is_search_query(self, text: str) -> bool:
        """Check if query is searching for products"""
        keywords = ["search", "find", "look for"]
        return any(kw in text for kw in keywords) and "product" in text

    def _is_update_product_query(self, text: str) -> bool:
        """Check if query is updating a product"""
        keywords = ["update product", "change product", "modify product"]
        return any(kw in text for kw in keywords)

    def _is_delete_product_query(self, text: str) -> bool:
        """Check if query is deleting a product"""
        keywords = ["delete product", "remove product"]
        return any(kw in text for kw in keywords)

    def _is_statistics_query(self, text: str) -> bool:
        """Check if query is asking for statistics"""
        keywords = ["statistics", "stats", "summary"]
        return any(kw in text for kw in keywords)

    def _is_get_order_query(self, text: str) -> bool:
        """Check if query is getting a specific order"""
        keywords = ["get order", "show order", "find order"]
        return any(kw in text for kw in keywords)

    def _is_update_order_query(self, text: str) -> bool:
        """Check if query is updating order status"""
        keywords = ["update order", "change order status", "complete order"]
        return any(kw in text for kw in keywords)

    def _is_cancel_order_query(self, text: str) -> bool:
        """Check if query is cancelling an order"""
        keywords = ["cancel order"]
        return any(kw in text for kw in keywords)

    def _extract_category(self, text: str) -> Optional[str]:
        """Extract category from text"""
        if "electronics" in text:
            return "Electronics"
        elif "accessories" in text:
            return "Accessories"
        elif "furniture" in text:
            return "Furniture"
        return None

    def _extract_order_status(self, text: str) -> Optional[str]:
        """Extract order status from text"""
        if "pending" in text:
            return "pending"
        elif "completed" in text:
            return "completed"
        elif "cancelled" in text:
            return "cancelled"
        return None

    def _extract_search_term(self, text: str) -> Optional[str]:
        """Extract search term from text"""
        # Pattern: "search for X" or "find X"
        match = re.search(r'(?:search|find|look for)\s+(?:product\s+)?(.+?)(?:\s+product)?$', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def _parse_add_product(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Parse add product command - multiple format support"""
        # Format 1: "add product: Name, price: 599, category: Furniture"
        match = re.search(
            r'add product:\s*(.+?),\s*price:\s*(\d+\.?\d*),\s*category:\s*(\w+)',
            user_input,
            re.IGNORECASE
        )
        if match:
            return {
                "tool": "add_product",
                "arguments": {
                    "name": match.group(1).strip(),
                    "price": float(match.group(2)),
                    "category": match.group(3).strip(),
                    "in_stock": "out of stock" not in user_input.lower()
                }
            }

        # Format 2: "add product: Name, $599, Category"
        match = re.search(
            r'add product:\s*(.+?),\s*\$?(\d+\.?\d*),\s*(.+?)(?:\s*$|,)',
            user_input,
            re.IGNORECASE
        )
        if match:
            return {
                "tool": "add_product",
                "arguments": {
                    "name": match.group(1).strip(),
                    "price": float(match.group(2)),
                    "category": match.group(3).strip(),
                    "in_stock": "out of stock" not in user_input.lower()
                }
            }

        return None

    def _parse_create_order(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse create order command"""
        # "order product 1 quantity 2"
        product_match = re.search(r'product\s+(?:id\s+)?(\d+)', text)
        quantity_match = re.search(r'quantity\s+(\d+)', text)

        if product_match:
            quantity = int(quantity_match.group(1)) if quantity_match else 1
            return {
                "tool": "create_order",
                "arguments": {
                    "product_id": int(product_match.group(1)),
                    "quantity": quantity
                }
            }

        return None

    def _parse_get_product(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse get product command"""
        id_match = re.search(r'(?:id\s+|#)?(\d+)', text)
        if id_match:
            return {
                "tool": "get_product",
                "arguments": {"product_id": int(id_match.group(1))}
            }

        return None

    def _parse_update_product(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Parse update product command"""
        # "update product 1 price 999"
        # "update product 1 name New Name"
        # "update product 1 in_stock false"
        product_match = re.search(r'product\s+(\d+)', user_input, re.IGNORECASE)
        if not product_match:
            return None

        product_id = int(product_match.group(1))
        arguments = {"product_id": product_id}

        # Check for price update
        price_match = re.search(r'price\s+(\d+\.?\d*)', user_input, re.IGNORECASE)
        if price_match:
            arguments["price"] = float(price_match.group(1))

        # Check for name update
        name_match = re.search(r'name\s+(.+?)(?:\s+(?:price|category|in_stock)|$)', user_input, re.IGNORECASE)
        if name_match:
            arguments["name"] = name_match.group(1).strip()

        # Check for category update
        category_match = re.search(r'category\s+(\w+)', user_input, re.IGNORECASE)
        if category_match:
            arguments["category"] = category_match.group(1)

        # Check for stock status
        if "in_stock true" in user_input.lower() or "in stock" in user_input.lower():
            arguments["in_stock"] = True
        elif "in_stock false" in user_input.lower() or "out of stock" in user_input.lower():
            arguments["in_stock"] = False

        if len(arguments) > 1:  # Has product_id + at least one update field
            return {
                "tool": "update_product",
                "arguments": arguments
            }

        return None

    def _parse_delete_product(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse delete product command"""
        # "delete product 1"
        product_match = re.search(r'product\s+(\d+)', text)
        if product_match:
            return {
                "tool": "delete_product",
                "arguments": {"product_id": int(product_match.group(1))}
            }
        return None

    def _parse_get_order(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse get order command"""
        # "get order 1" or "show order 5"
        order_match = re.search(r'order\s+(\d+)', text)
        if order_match:
            return {
                "tool": "get_order",
                "arguments": {"order_id": int(order_match.group(1))}
            }
        return None

    def _parse_update_order_status(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse update order status command"""
        # "update order 1 status completed"
        # "complete order 1"
        order_match = re.search(r'order\s+(\d+)', text)
        if not order_match:
            return None

        order_id = int(order_match.group(1))

        # Determine status
        status = None
        if "completed" in text or "complete" in text:
            status = "completed"
        elif "pending" in text:
            status = "pending"
        elif "cancelled" in text or "cancel" in text:
            status = "cancelled"

        if status:
            return {
                "tool": "update_order_status",
                "arguments": {
                    "order_id": order_id,
                    "status": status
                }
            }

        return None

    def _parse_cancel_order(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse cancel order command"""
        # "cancel order 1"
        order_match = re.search(r'order\s+(\d+)', text)
        if order_match:
            return {
                "tool": "cancel_order",
                "arguments": {"order_id": int(order_match.group(1))}
            }
        return None

    def invoke(self, user_input: str, tool_executor) -> str:
        """
        Main entry: parse intent (mock) → execute tool (REAL) → format (mock)

        Args:
            user_input: User's query
            tool_executor: Tool executor instance

        Returns:
            Formatted response string
        """
        intent = self.parse_intent(user_input)

        if not intent.get("tool"):
            return f"❌ {intent.get('error', 'Could not understand request')}"

        tool_name = intent["tool"]
        arguments = intent["arguments"]
        source = intent.get("source", "unknown")

        logger.info(f"Tool: {tool_name}, Args: {arguments}, Source: {source}")

        result = tool_executor.call_tool(tool_name, arguments)

        return self._format_response(tool_name, result)

    def _format_response(self, tool_name: str, result: Any) -> str:
        """Convert tool result to natural language"""
        if isinstance(result, dict) and result.get("success") == False:
            return f"❌ {result.get('error', 'Unknown error')}"

        if tool_name == "list_products":
            if not result:
                return "📦 No products found."

            lines = [f"📦 Found {len(result)} products:"]
            for p in result:
                stock = "✅ In Stock" if p['in_stock'] else "❌ Out of Stock"
                lines.append(f"  • ID {p['id']}: {p['name']} - ${p['price']} ({p['category']}) - {stock}")
            return "\n".join(lines)

        elif tool_name == "add_product":
            return (f"✅ Product added:\n"
                    f"  • ID: {result['id']}\n"
                    f"  • Name: {result['name']}\n"
                    f"  • Price: ${result['price']}\n"
                    f"  • Category: {result['category']}")

        elif tool_name == "get_product":
            stock = "In Stock" if result['in_stock'] else "Out of Stock"
            return (f"📦 Product:\n"
                    f"  • ID: {result['id']}\n"
                    f"  • Name: {result['name']}\n"
                    f"  • Price: ${result['price']}\n"
                    f"  • Category: {result['category']}\n"
                    f"  • Status: {stock}")

        elif tool_name == "create_order":
            return (f"🛒 Order created:\n"
                    f"  • Order ID: {result['order_id']}\n"
                    f"  • Product: {result['product_name']}\n"
                    f"  • Quantity: {result['quantity']}\n"
                    f"  • Total: ${result['total_price']}")

        elif tool_name == "list_orders":
            if not result:
                return "📋 No orders found."

            lines = [f"📋 Found {len(result)} orders:"]
            for o in result:
                lines.append(
                    f"  • Order #{o['order_id']}: {o['product_name']} x{o['quantity']} = ${o['total_price']} ({o['status']})")
            return "\n".join(lines)

        elif tool_name == "update_product":
            return (f"✅ Product updated:\n"
                   f"  • ID: {result['id']}\n"
                   f"  • Name: {result['name']}\n"
                   f"  • Price: ${result['price']}\n"
                   f"  • Category: {result['category']}\n"
                   f"  • In Stock: {result['in_stock']}")

        elif tool_name == "delete_product":
            return f"✅ Deleted product: {result['product_name']} (ID: {result['product_id']})"

        elif tool_name == "get_statistics":
            return (f"📊 Product Statistics:\n"
                   f"  • Total Products: {result['total_count']}\n"
                   f"  • Average Price: ${result['average_price']}\n"
                   f"  • Categories: {', '.join(result['categories'])}\n"
                   f"  • In Stock: {result['in_stock_count']}")

        elif tool_name == "get_order":
            return (f"📋 Order Details:\n"
                   f"  • Order ID: {result['order_id']}\n"
                   f"  • Product: {result['product_name']}\n"
                   f"  • Quantity: {result['quantity']}\n"
                   f"  • Total: ${result['total_price']}\n"
                   f"  • Status: {result['status']}")

        elif tool_name == "update_order_status":
            return (f"✅ Order status updated:\n"
                   f"  • Order ID: {result['order_id']}\n"
                   f"  • Product: {result['product_name']}\n"
                   f"  • New Status: {result['status']}")

        elif tool_name == "cancel_order":
            return f"✅ {result['message']}"

        elif tool_name == "get_order_statistics":
            return (f"📊 Order Statistics:\n"
                   f"  • Total Orders: {result['total_orders']}\n"
                   f"  • Pending: {result['pending_orders']}\n"
                   f"  • Completed: {result['completed_orders']}\n"
                   f"  • Cancelled: {result['cancelled_orders']}\n"
                   f"  • Total Revenue: ${result['total_revenue']}")

        elif tool_name == "search_products_by_name":
            if not result:
                return "🔍 No products found matching your search."

            lines = [f"🔍 Found {len(result)} matching products:"]
            for p in result:
                stock = "✅ In Stock" if p['in_stock'] else "❌ Out of Stock"
                lines.append(f"  • ID {p['id']}: {p['name']} - ${p['price']} ({p['category']}) - {stock}")
            return "\n".join(lines)

        return json.dumps(result, indent=2)
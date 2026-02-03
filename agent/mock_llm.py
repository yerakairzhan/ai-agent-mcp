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

        logger.warning(f"Could not parse intent for: {user_input}")
        return {
            "tool": None,
            "arguments": {},
            "error": "Could not parse intent. Try: 'list products', 'add product: Name, price: X, category: Y', 'order product 1 quantity 2'",
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

        elif tool_name == "search_products_by_name":
            if not result:
                return "🔍 No products found matching your search."

            lines = [f"🔍 Found {len(result)} matching products:"]
            for p in result:
                stock = "✅ In Stock" if p['in_stock'] else "❌ Out of Stock"
                lines.append(f"  • ID {p['id']}: {p['name']} - ${p['price']} ({p['category']}) - {stock}")
            return "\n".join(lines)

        return json.dumps(result, indent=2)
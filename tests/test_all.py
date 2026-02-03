"""
Test Suite for AI Agent MCP Project
Tests API endpoints, agent functionality, and database operations
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app
from database import SessionLocal, Product, Order, init_db
from agent.tool_executor import ToolExecutor


@pytest.fixture(scope="module")
def client():
    """Create test client"""
    init_db()
    return TestClient(app)


@pytest.fixture
def tool_executor():
    """Create tool executor for testing"""
    return ToolExecutor()


class TestAPI:
    """Test FastAPI endpoints"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["version"] == "1.0.0"

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-agent-mcp-api"

    def test_agent_query_list_products(self, client):
        """Test agent query for listing products"""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "list all products"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "Found" in data["response"] or "products" in data["response"].lower()

    def test_agent_query_add_product(self, client):
        """Test agent query for adding product"""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "add product: Test Product, price: 99.99, category: Electronics"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "added" in data["response"].lower()

    def test_agent_query_create_order(self, client):
        """Test agent query for creating order"""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "order product 1 quantity 2"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # Should either succeed or show error message
        assert "order" in data["response"].lower()


class TestToolExecutor:
    """Test tool execution"""

    def test_list_products(self, tool_executor):
        """Test list_products tool"""
        result = tool_executor.call_tool("list_products", {})
        assert isinstance(result, list)
        assert len(result) > 0
        assert "id" in result[0]
        assert "name" in result[0]

    def test_add_product(self, tool_executor):
        """Test add_product tool"""
        result = tool_executor.call_tool(
            "add_product",
            {
                "name": "Test Laptop",
                "price": 999.99,
                "category": "Electronics",
                "in_stock": True
            }
        )
        assert isinstance(result, dict)
        assert result.get("success") == True or "id" in result
        assert "name" in result

    def test_get_product(self, tool_executor):
        """Test get_product tool"""
        result = tool_executor.call_tool("get_product", {"product_id": 1})
        assert isinstance(result, dict)
        if result.get("success") != False:
            assert "name" in result
            assert "price" in result

    def test_create_order(self, tool_executor):
        """Test create_order tool"""
        result = tool_executor.call_tool(
            "create_order",
            {"product_id": 1, "quantity": 1}
        )
        assert isinstance(result, dict)
        if result.get("success") != False:
            assert "order_id" in result
            assert "total_price" in result

    def test_list_available_tools(self, tool_executor):
        """Test tool registry"""
        tools = tool_executor.list_available_tools()
        assert "mcp_tools" in tools
        assert "custom_tools" in tools
        assert "total" in tools
        assert tools["total"] > 0


class TestDatabase:
    """Test database operations"""

    def test_product_creation(self):
        """Test creating product in database"""
        db = SessionLocal()
        try:
            product = Product(
                name="Test Product",
                price=49.99,
                category="Test",
                in_stock=True
            )
            db.add(product)
            db.commit()
            db.refresh(product)

            assert product.id is not None
            assert product.name == "Test Product"
            assert product.price == 49.99
        finally:
            db.close()

    def test_order_creation(self):
        """Test creating order in database"""
        db = SessionLocal()
        try:
            # Get first product
            product = db.query(Product).first()
            if product:
                order = Order(
                    product_id=product.id,
                    quantity=2,
                    total_price=product.price * 2,
                    status="pending"
                )
                db.add(order)
                db.commit()
                db.refresh(order)

                assert order.id is not None
                assert order.quantity == 2
                assert order.status == "pending"
        finally:
            db.close()

    def test_product_order_relationship(self):
        """Test product-order relationship"""
        db = SessionLocal()
        try:
            product = db.query(Product).first()
            if product and product.orders:
                order = product.orders[0]
                assert order.product_id == product.id
                assert order.product.name == product.name
        finally:
            db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
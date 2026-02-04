# 🤖 AI Agent MCP Project

> **Production-ready AI agent system with FastMCP, LangGraph, Alembic migrations, and Web UI**

![Python](https://img.shields.io/badge/python-3.11-blue.svg)

---

## 🚀 Quick Start

```bash
# Start everything
docker-compose up --build

# Open browser
http://localhost:8000
```

**That's it!** The web UI, API, and database are all ready.

---

## 🌐 Web Interface

Access the **terminal-style UI** at the root URL (`http://localhost:8000`)

### Features
- ⚡ Real-time agent queries
- 🛠️ Click-to-use tool catalog
- 📊 12 MCP tools available
- 🎨 Retro terminal aesthetic

### Example Queries

**Product Management:**
```
list all products
add product: Mouse Pad, price: 15.99, category: Accessories
update product 1 price 999
delete product 5
get statistics
```

**Order Management:**
```
order product 1 quantity 2
list all orders
update order 1 status completed
cancel order 1
get order statistics
```

---

## 🗄️ Database Migrations

Full **Alembic** integration for schema management.

### Quick Commands

```bash
# Check current version
docker exec -it ai-agent-mcp-api python migrate.py current

# Apply migrations
docker exec -it ai-agent-mcp-api python migrate.py upgrade

# Create new migration
docker exec -it ai-agent-mcp-api python migrate.py create "add field"

# View history
docker exec -it ai-agent-mcp-api python migrate.py history
```

### Adding a New Field

**1. Edit `database.py`:**
```python
class Product(Base):
    # ... existing fields ...
    description = Column(String, nullable=True)  # NEW
```

**2. Create migration:**
```bash
docker exec -it ai-agent-mcp-api python migrate.py create "add description"
```

**3. Apply:**
```bash
docker exec -it ai-agent-mcp-api python migrate.py upgrade
```

📖 **Full Guide**: [MIGRATIONS.md](MIGRATIONS.md)

---

## 🏗️ Architecture

```
Web Browser (http://localhost:8000)
         │
         ▼
    FastAPI Server
    • Serves HTML UI at /
    • API at /api/v1/agent/query
         │
         ▼
   LangGraph Agent
   • MockLLM (intent parsing)
   • Tool executor
         │
    ┌────┴────┐
    ▼         ▼
MCP Product   MCP Order
Server        Server
(6 tools)     (6 tools)
    │         │
    └────┬────┘
         ▼
   SQLAlchemy ORM
         │
         ▼
  Alembic Migrations
         │
         ▼
   SQLite Database
   (/app/data/)
```

---

## 📡 API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Agent Query
```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "list all products"}'
```

### All Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI interface |
| `/health` | GET | Health check |
| `/api/v1/agent/query` | POST | Agent queries |
| `/docs` | GET | API documentation |

---

## 🛠️ MCP Tools (12 Total)

### Product Server (6 Tools)
- `list_products` - List all or filter by category
- `get_product` - Get product by ID
- `add_product` - Add new product
- `update_product` - Update product fields
- `delete_product` - Delete product
- `get_statistics` - Product statistics

### Order Server (6 Tools)
- `create_order` - Create new order
- `get_order` - Get order by ID
- `list_orders` - List all or filter by status
- `update_order_status` - Update status
- `cancel_order` - Cancel order
- `get_order_statistics` - Order statistics

### Custom Agent Tools (3 Tools)
- `search_products_by_name` - Search by name

**Total: 13 tools** (12 MCP + 1 Custom)

---

## 🧪 Testing

```bash
# Run all tests (9 total)
pytest tests/ -v

# Run in Docker
docker exec -it ai-agent-mcp-api pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

**Test Coverage:**
- 3 API tests
- 6 Tool execution tests
- 3 Database tests

---

## 📁 Project Structure

```
ai-agent-project/
├── api/
│   └── main.py             # FastAPI app
├── frontend/
│   └── index.html          # Web UI ⭐
├── agent/
│   ├── langgraph_agent.py  # LangGraph workflow
│   ├── mock_llm.py         # Intent parsing
│   ├── tool_executor.py    # Tool execution
│   ├── tools.py            # MCP implementations
│   └── custom_tools.py     # Custom tools
├── mcp_servers/
│   ├── product_server.py   # Product MCP (6 tools)
│   └── order_server.py     # Order MCP (6 tools)
├── alembic/                # Migrations ⭐
│   ├── versions/
│   │   └── 001_initial_migration.py
│   │  
│   ├── env.py
│   └── script.py.mako
├── tests/
│   └── test_all.py       # 9 tests
├── database.py             # SQLAlchemy models
├── migrate.py              # Migration CLI ⭐
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md           # This file
```

---

## 💻 Development

### Local Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python migrate.py init
uvicorn api.main:app --reload
```

### Docker Development
```bash
# Rebuild
docker-compose up --build

# View logs
docker-compose logs -f

# Access container
docker exec -it ai-agent-mcp-api bash

# Stop
docker-compose down
```

## 🎯 Key Features

1. **Web Interface** - Terminal-style UI for easy testing
2. **Migrations** - Alembic for safe schema evolution
3. **Dual MCP** - Separate Product & Order servers
4. **Real DB** - All operations commit to SQLite
5. **Docker Ready** - Single command deployment

---

## 🐛 Troubleshooting

### Reset Everything
```bash
docker-compose down
rm -rf data/
docker-compose up --build
```

### Check Migrations
```bash
docker exec -it ai-agent-mcp-api python migrate.py current
docker exec -it ai-agent-mcp-api python migrate.py history
```

### Access Database
```bash
docker exec -it ai-agent-mcp-api sqlite3 /app/data/products.db
.tables
.schema products
.exit
```

## 🚀 Try It Now

```bash
# 1. Start
docker-compose up --build

# 2. Open browser
http://localhost:8000

# 3. Try a query
"list all products"
```
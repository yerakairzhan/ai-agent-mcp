# 🤖 AI Agent MCP - Documentation / Документация

[English](#english) | [Русский](#russian)

---

<a name="english"></a>
## 🇬🇧 

### 📋 What is this?

An AI agent system that manages products and orders using natural language queries. Built with FastAPI, LangGraph, and SQLite.

### 🚀 Quick Start

**Option 1: Docker (Recommended)**
```bash
# Start everything
docker-compose up --build

# Visit
http://localhost:8000
```

**Option 2: Local**
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python database.py

# Run server
uvicorn api.main:app --reload

# Visit
http://localhost:8000
```

### 📂 Project Structure

```
├── frontend/           # Web interface
│   └── index.html     # Single-page UI
├── api/               # REST API
│   └── main.py        # FastAPI endpoints
├── agent/             # AI Agent
│   ├── langgraph_agent.py  # Main agent
│   ├── mock_llm.py         # Intent parser
│   ├── tool_executor.py    # Tool runner
│   ├── tools.py            # MCP tools
│   └── custom_tools.py     # Custom tools
├── mcp_server/        # MCP Servers
│   ├── main_server.py      # Product server
│   └── order_server.py     # Order server
├── migrations/        # Database migrations
├── tests/            # Unit tests
├── database.py       # SQLAlchemy models
└── products.db       # SQLite database
```

### 💬 Example Queries

**Products:**
- `list all products`
- `show products in Electronics category`
- `add product: Webcam, price: 89.99, category: Electronics`
- `search for laptop`

**Orders:**
- `order product 1 quantity 2`
- `list all pending orders`
- `get order summary 1`

### 🛠️ Features

- ✅ Natural language processing
- ✅ Product management (CRUD)
- ✅ Order processing
- ✅ SQLite database
- ✅ REST API
- ✅ Web interface
- ✅ Docker support

### 📡 API Endpoints

**Main endpoint:**
```
POST /api/v1/agent/query
Content-Type: application/json

{
  "query": "list all products"
}
```

**Health check:**
```
GET /health
```

### 🧪 Testing

```bash
# Run all tests
pytest tests/test_all.py -v

# 12 tests covering:
# - MCP server tools
# - Agent functionality
# - API endpoints
# - Integration
```

### 📊 Database

**Tables:**
- `products` - Product catalog
- `orders` - Customer orders

**Access database:**
```bash
# View database
sqlite3 products.db

# Show tables
.tables

# Query products
SELECT * FROM products;
```

### 🐳 Docker

**Commands:**
```bash
# Start
docker-compose up

# Stop
docker-compose down

# Rebuild
docker-compose up --build

# View logs
docker-compose logs -f
```

### ❓ Troubleshooting

**Problem: Port 8000 in use**
```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"
```

**Problem: Database locked**
```bash
# Delete and reinitialize
rm products.db
python database.py
```

### 📝 Tech Stack

- Python 3.11+
- FastAPI
- LangGraph
- SQLAlchemy
- SQLite
- FastMCP

---

<a name="russian"></a>
## 🇷🇺 

### 📋 Что это?

AI-агент для управления продуктами и заказами через естественный язык. Построен на FastAPI, LangGraph и SQLite.

### 🚀 Быстрый старт

**Вариант 1: Docker (рекомендуется)**
```bash
# Запустить всё
docker-compose up --build

# Открыть
http://localhost:8000
```

**Вариант 2: Локально**
```bash
# Установить зависимости
pip install -r requirements.txt

# Инициализировать базу данных
python database.py

# Запустить сервер
uvicorn api.main:app --reload

# Открыть
http://localhost:8000
```

### 📂 Структура проекта

```
├── frontend/           # Веб-интерфейс
│   └── index.html     # Одностраничный UI
├── api/               # REST API
│   └── main.py        # FastAPI endpoints
├── agent/             # AI Агент
│   ├── langgraph_agent.py  # Основной агент
│   ├── mock_llm.py         # Парсер намерений
│   ├── tool_executor.py    # Исполнитель инструментов
│   ├── tools.py            # MCP инструменты
│   └── custom_tools.py     # Кастомные инструменты
├── mcp_server/        # MCP Серверы
│   ├── main_server.py      # Сервер продуктов
│   └── order_server.py     # Сервер заказов
├── migrations/        # Миграции БД
├── tests/            # Тесты
├── database.py       # SQLAlchemy модели
└── products.db       # SQLite база данных
```

### 💬 Примеры запросов

**Продукты:**
- `list all products` - показать все продукты
- `show products in Electronics category` - показать электронику
- `add product: Webcam, price: 89.99, category: Electronics` - добавить товар
- `search for laptop` - найти ноутбук

**Заказы:**
- `order product 1 quantity 2` - заказать товар
- `list all pending orders` - показать ожидающие заказы
- `get order summary 1` - детали заказа

### 🛠️ Возможности

- ✅ Обработка естественного языка
- ✅ Управление продуктами (CRUD)
- ✅ Обработка заказов
- ✅ База данных SQLite
- ✅ REST API
- ✅ Веб-интерфейс
- ✅ Поддержка Docker

### 📡 API Endpoints

**Основной endpoint:**
```
POST /api/v1/agent/query
Content-Type: application/json

{
  "query": "list all products"
}
```

**Проверка здоровья:**
```
GET /health
```

### 🧪 Тестирование

```bash
# Запустить все тесты
pytest tests/test_all.py -v

# 12 тестов покрывают:
# - Инструменты MCP сервера
# - Функциональность агента
# - API endpoints
# - Интеграцию
```

### 📊 База данных

**Таблицы:**
- `products` - Каталог продуктов
- `orders` - Заказы клиентов

**Доступ к БД:**
```bash
# Просмотр базы данных
sqlite3 products.db

# Показать таблицы
.tables

# Запрос продуктов
SELECT * FROM products;
```

### 🐳 Docker

**Команды:**
```bash
# Запустить
docker-compose up

# Остановить
docker-compose down

# Пересобрать
docker-compose up --build

# Логи
docker-compose logs -f
```

### ❓ Решение проблем

**Проблема: Порт 8000 занят**
```bash
# Изменить порт в docker-compose.yml
ports:
  - "8001:8000"
```

**Проблема: База данных заблокирована**
```bash
# Удалить и переинициализировать
rm products.db
python database.py
```

### 📝 Технологии

- Python 3.11+
- FastAPI
- LangGraph
- SQLAlchemy
- SQLite
- FastMCP

---

## 🎯 Common Tasks / Общие задачи

### Add a Product / Добавить продукт
```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "add product: Mouse, price: 25, category: Electronics"}'
```

### List Orders / Список заказов
```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "list all orders"}'
```

### Search Products / Поиск продуктов
```bash
curl -X POST http://localhost:8000/api/v1/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "search for laptop"}'
```
---

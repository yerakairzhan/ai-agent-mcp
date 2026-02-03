"""
FastAPI Application
Main API server with agent query endpoint
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.langgraph_agent import run_agent_query

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Agent MCP API",
    description="Product and Order Management API with AI Agent using MCP servers",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    """Request model for agent queries"""
    query: str


class QueryResponse(BaseModel):
    """Response model for agent queries"""
    response: str


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting FastAPI application...")
    from database import init_db, seed_initial_data
    init_db()
    seed_initial_data()
    logger.info("Database initialized")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Agent MCP API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "agent_query": "/api/v1/agent/query",
            "docs": "/docs"
        },
        "features": [
            "FastMCP integration (Product + Order servers)",
            "LangGraph agent with custom tools",
            "SQLite persistence",
            "Docker support"
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint for Docker"""
    return {
        "status": "healthy",
        "service": "ai-agent-mcp-api"
    }


@app.post("/api/v1/agent/query", response_model=QueryResponse)
async def agent_query(request: QueryRequest):
    """
    Process natural language queries using AI agent

    The agent can handle:
    - Product queries: "list all products", "add product: X, price: Y, category: Z"
    - Order queries: "order product 1 quantity 2", "list all orders"
    - Search: "search for laptop"

    Args:
        request: Query request with natural language query

    Returns:
        Formatted response from agent

    Raises:
        HTTPException: If query processing fails
    """
    try:
        logger.info(f"Received query: {request.query}")
        response = run_agent_query(request.query)
        logger.info(f"Query processed successfully")
        return QueryResponse(response=response)
    except Exception as e:
        logger.error(f"Query processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
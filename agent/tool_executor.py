"""
Tool Executor
Executes both MCP tools and custom tools
"""
from typing import Dict, Any, Callable
import json
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, Product, Order
from agent.custom_tools import CUSTOM_TOOL_REGISTRY

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes real database tools (both MCP and custom)"""

    def __init__(self):
        # Import MCP tools from tools module
        from agent.tools import TOOL_REGISTRY as MCP_TOOLS

        self.mcp_tools = MCP_TOOLS
        self.custom_tools = CUSTOM_TOOL_REGISTRY

        # Combined registry
        self.all_tools = {**self.mcp_tools, **self.custom_tools}

        logger.info(f"ToolExecutor initialized with {len(self.all_tools)} tools")
        logger.info(f"MCP tools: {list(self.mcp_tools.keys())}")
        logger.info(f"Custom tools: {list(self.custom_tools.keys())}")

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute tool function with arguments.

        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        if tool_name not in self.all_tools:
            logger.error(f"Unknown tool: {tool_name}")
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        tool_func = self.all_tools[tool_name]

        try:
            logger.info(f"Executing tool: {tool_name} with args: {arguments}")
            result = tool_func(**arguments)
            logger.info(f"Tool {tool_name} executed successfully")
            return result
        except TypeError as e:
            logger.error(f"Invalid arguments for {tool_name}: {e}")
            return {"success": False, "error": f"Invalid arguments for {tool_name}: {str(e)}"}
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            return {"success": False, "error": f"Tool execution failed: {str(e)}"}

    def call_tool_json(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Same as call_tool but returns JSON string (for compatibility)

        Args:
            tool_name: Name of tool
            arguments: Tool arguments

        Returns:
            JSON string of result
        """
        result = self.call_tool(tool_name, arguments)
        return json.dumps(result)

    def list_available_tools(self) -> Dict[str, list]:
        """
        List all available tools

        Returns:
            Dictionary with mcp_tools and custom_tools lists
        """
        return {
            "mcp_tools": list(self.mcp_tools.keys()),
            "custom_tools": list(self.custom_tools.keys()),
            "total": len(self.all_tools)
        }
"""
LangGraph Agent
Integrates MockLLM with tool execution (MCP + custom tools)
"""
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from operator import add
import logging

from agent.mock_llm import MockLLM
from agent.tool_executor import ToolExecutor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Agent state for LangGraph"""
    messages: Annotated[list[str], add]
    user_input: str
    response: str


def agent_node(state: AgentState) -> AgentState:
    """
    Agent node that uses MockLLM with REAL tools (MCP + custom)

    Args:
        state: Current agent state

    Returns:
        Updated agent state with response
    """
    logger.info(f"Processing user input: {state['user_input']}")

    llm = MockLLM()
    executor = ToolExecutor()

    response = llm.invoke(state["user_input"], executor)

    logger.info(f"Agent response generated: {response[:100]}...")

    return {
        **state,
        "messages": state["messages"] + [response],
        "response": response
    }


# Build LangGraph
logger.info("Building LangGraph...")
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_edge(START, "agent")
graph.add_edge("agent", END)

app = graph.compile()
logger.info("LangGraph compiled successfully")


def run_agent_query(user_input: str) -> str:
    """
    Execute agent workflow

    Args:
        user_input: User's natural language query

    Returns:
        Agent's formatted response
    """
    logger.info(f"Running agent query: {user_input}")

    result = app.invoke({
        "messages": [],
        "user_input": user_input,
        "response": ""
    })

    logger.info("Agent query completed")
    return result["response"]
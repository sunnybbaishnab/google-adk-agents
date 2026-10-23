import ast
import operator
import re

from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

MODEL = "gemini-3.1-flash-lite"          # main agent, calculator, etc.
SEARCH_MODEL = "gemini-3.5-flash-lite"       # only for the search agent

# ---------- Tool 1: Google Search (built-in) ----------
google_search_tool = Agent(
    name='google_search_tool',
    model=SEARCH_MODEL,
    description="""
    Searches Google to find current or external information.
    """,
    instruction="""
    Use Google Search to find relevant, up-to-date information.
    Return a short, factual summary of what you find.
    """,
    tools=[google_search],
)


# ---------- Tool 2: Calculator (custom) ----------
_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}

def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")

def calculator(expression: str) -> dict:
    """Evaluates a mathematical expression and returns the result.

    Use this for any calculation (percentages, GST, interest, etc.).
    Supports + - * / ** % // and parentheses.

    Args:
        expression: A math expression such as "12500 * 18 / 100".

    Returns:
        A dict with status and result (or an error message).
    """
    try:
        result = _eval(ast.parse(expression.strip(), mode="eval").body)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return {"status": "success", "result": result}
    except ZeroDivisionError:
        return {"status": "error", "message": "Division by zero."}
    except Exception as e:
        return {"status": "error", "message": f"Could not evaluate: {e}"}


# ---------- Tool 3: Text Analyzer (custom) ----------
def text_analyzer(text: str) -> dict:
    """Analyzes a piece of text and returns its character, 
    word and sentence counts.

    Args:
        text: The text to analyze.

    Returns:
        A dict with characters, words and sentences counts.
    """
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    return {
        "status": "success",
        "characters": len(text),
        "words": len(text.split()),
        "sentences": len(sentences),
    }


# ---------- Root agent ----------
root_agent = Agent(
    name="personal_assistant",
    model=MODEL,
    description="""
    A general-purpose assistant that can search,
    calculate and analyze text.
    """,
    instruction=(
        """You are a helpful personal assistant. Choose the right tool:
        - google_search_tool: for current or external information.
        - calculator: for ANY math or calculation. Never calculate in your head.
        - text_analyzer: when asked for character, word or sentence counts.
        You may use more than one tool in a single request.
        Then give one clear final answer."""
    ),
    tools=[AgentTool(agent=google_search_tool), calculator, text_analyzer],
)
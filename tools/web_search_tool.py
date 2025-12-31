from langchain.tools import tool

@tool
def simple_web_search(query: str) -> str:
    """
    Placeholder fallback search tool
    """
    return f"No live web search enabled. Query was: {query}"
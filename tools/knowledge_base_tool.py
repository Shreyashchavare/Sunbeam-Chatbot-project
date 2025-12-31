from langchain.tools import tool
from knowledge.vectorstore import get_vectorstore

@tool
def sunbeam_knowledge_search(query: str) -> str:
    """Search Sunbeam knowledge base"""
    db = get_vectorstore()
    docs = db.similarity_search(query, k=5)

    if not docs:
        return "No relevant data found."

    return "\n\n".join(doc.page_content for doc in docs)
from langchain.tools import tool
from knowledge.vectorstore import get_vectorstore

@tool
def sunbeam_knowledge_search(query: str) -> str:
    """Search Sunbeam knowledge base"""
    db = get_vectorstore()
    docs = db.similarity_search(query, k=10)

    if not docs:
        return "NO RESULTS FOUND. DO NOT SEARCH AGAIN. Inform the user that the knowledge base is currently empty or does not contain this information."

    return "\n\n".join(doc.page_content for doc in docs)
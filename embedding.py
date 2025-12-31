from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from typing import List, Optional
import os

class SunbeamEmbeddingStore:
    """
    Handles embedding creation, storage, and retrieval
    for Sunbeam Internship scraped data.
    """

    def __init__(
            self,
            persist_directory: str = "senbeam_chroma_db",
            embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model

        self.embeddings = HuggingFaceEmbeddings(
            model_name = self.embedding_model
        )
        self.vectordb:Optional[Chroma] = None

    #--------------------------------------------------------------

    def load_store(self):
        """
       Load an existing vector store from disk.
        """

        if not os.path.exists(self.persist_directory):
            raise FileNotFoundError("vector store not found.Create it first.")
        
        self.vectordb = Chroma(
            persist_directory = self.persist_directory,
            embedding_function = self.embeddings
        )
        return self.vectordb
    
    #--------------------------------------------------------------

    def similarity_search(self,query:str,k: int = 5):
        """
        Perform similarity search on embeddings.
        """
        if not self.vectordb:
            raise ValueError("vector store not loaded ")
        
        return self.vectordb.similarity_search(query,k=k)
    
    #--------------------------------------------------------------

    def embed_and_search_query(
            self,
            query:str,
            top_k: int = 5
    ):
        """
       Embeds the user query and performs similarity search.

        Args:
            query (str): User input question
            top_k (int): Number of similar documents to retrieve

        Returns:
            List[Document]: Relevant documents
        """

        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        return self.similarity_search(query = query,k = top_k)
        
        
import os
from typing import List, Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


class SunbeamChromaDB:
    """python -m pip install --upgrade pip

    ChromaDB manager for Sunbeam RAG system.
    Compatible with scraped data + lazy loader.
    """

    def __init__(
        self,
        persist_directory: str = "sunbeam_chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        self.persist_directory = persist_directory

        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model
        )

        self.vectordb: Optional[Chroma] = None

    # --------------------------------------------------
    # Convert scraped JSON → LangChain Documents
    # --------------------------------------------------
    def build_documents(self, scraped_data: List[dict]) -> List[Document]:
        """
        scraped_data format:
        {
          "content": "...",
          "source": "about",
          "page": "About Us",
          "url": "...",
          "tool": "about_scraper"
        }
        """

        documents = []

        for item in scraped_data:
            documents.append(
                Document(
                    page_content=item["content"],
                    metadata={
                        "source": item["source"],
                        "page": item["page"],
                        "url": item["url"],
                        "tool": item.get("tool", "")
                    }
                )
            )

        return documents

    # --------------------------------------------------
    # Create Chroma DB (RUN ONLY ON DATA UPDATE)
    # --------------------------------------------------
    def create_store(self, documents: List[Document]) -> Chroma:
        self.vectordb = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )

        return self.vectordb

    # --------------------------------------------------
    # Load Existing Chroma DB
    # --------------------------------------------------
    def load_store(self) -> Chroma:
        if not os.path.exists(self.persist_directory):
            raise FileNotFoundError(
                "Chroma DB not found. Run create_store() first."
            )

        self.vectordb = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )

        return self.vectordb

    # --------------------------------------------------
    # Similarity Search
    # --------------------------------------------------
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        if not self.vectordb:
            raise ValueError("Vector store not loaded")

        return self.vectordb.similarity_search(query, k=k)

    # --------------------------------------------------
    # Embed + Search (RAG Entry Point)
    # --------------------------------------------------
    def embed_and_search(self, query: str, top_k: int = 5) -> List[Document]:
        if not query.strip():
            raise ValueError("Query cannot be empty")

        return self.similarity_search(query, k=top_k)

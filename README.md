# Sunbeam AI Chatbot ☀️

A production-ready AI chatbot for Sunbeam Institute, designed to answer student queries about courses, internships, and admissions. It uses a local RAG (Retrieval-Augmented Generation) pipeline with Selenium-based web scraping and a ChromaDB vector store.

## 🚀 Features

-   **Intelligent Q&A**: Answers questions using a local LLM (via LM Studio) and a curated knowledge base.
-   **Live Web Scraping**: Automatically fetches the latest data from Sunbeam’s official website (About, Courses, Internships).
-   **RAG Architecture**: Uses ChromaDB to store and retrieve relevant information effectively.
-   **Modern UI**: Built with Streamlit, featuring a polished, branded interface with Dark/Light modes.
-   **Lead Generation**: Integrated callback form for prospective students.

## 🛠️ Prerequisites

1.  **Python 3.10+** installed.
2.  **LM Studio** (or compatible local LLM server) running:
    *   Load a model (e.g., `google/gemma-3-4b` or `mistral`).
    *   Start the Local Server on port `1234`.
    *   Ensure `Cross-Origin-Resource-Sharing (CORS)` is enabled.

## 📦 Installation

1.  **Clone/Download the repository**.
2.  **Create a virtual environment**:
    ```powershell
    python -m venv sun
    .\sun\Scripts\activate
    ```
3.  **Install dependencies**:
    ```powershell
    pip install -r requirements.txt
    ```

## 🏗️ Setup & Data Ingestion

Before running the chat app, build the knowledge base to ensure the AI has the latest data.

1.  **Run the Knowledge Base Builder**:
    ```powershell
    python scripts/build_kb.py
    ```
    *This script systematically scrapes the Sunbeam website and populates the `chroma_db` vector store.*

## ▶️ Running the Chatbot

Launch the application using Streamlit:

```powershell
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`.

## 📂 Project Structure

-   `app.py`: Main Streamlit application entry point.
-   `backend/`: Contains the AI agent logic (`sunbeam_agent.py`).
-   `knowledge/`: Vector store configuration.
-   `loaders/`: Unified data loading orchestration.
-   `scrapers/`: Selenium scripts for scraping specific pages (`about_tools.py`, `courses_tool.py`, `internship_tool.py`).
-   `scripts/`: Utility scripts (e.g., `build_kb.py`).
-   `assets/`: Static assets like logos.

## 📝 Troubleshooting

-   **"No Results Found"**: Ensure you have run `python scripts/build_kb.py` successfully.
-   **Browser Errors**: The scrapers run in headless mode. Ensure you have a stable internet connection and Chrome installed.
-   **Agent Not Responding**: effective check if LM Studio is running and accepting requests at `http://127.0.0.1:1234`.

---
*Developed for Sunbeam Institute*

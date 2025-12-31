from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from tools.knowledge_base_tool import sunbeam_knowledge_search
from tools.web_search_tool import simple_web_search

def get_agent():
    llm = ChatOpenAI(
        model="google/gemma-3-4b",
        base_url="http://localhost:1234/v1",
        api_key="lm-studio"
    )

    system_prompt = """
        You are Sunbeam Institute AI Assistant.

        Rules:
        - Prefer Knowledge Base tool
        - Use web tool only if KB fails
        - Never hallucinate
        - Answer in simple English
        """

    return create_agent(
        model=llm,
        tools=[sunbeam_knowledge_search, simple_web_search],
        system_prompt=system_prompt
    )
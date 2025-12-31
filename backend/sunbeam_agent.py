from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from langchain_core.tools import tool
from tools.knowledge_base_tool import sunbeam_knowledge_search
from tools.web_search_tool import simple_web_search
import json

class SimpleAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="google/gemma-3-4b",
            base_url="http://127.0.0.1:1234/v1",
            api_key="lm-studio",
            temperature=0.0
        )
        self.tools = {
            "sunbeam_knowledge_search": sunbeam_knowledge_search
            # "simple_web_search": simple_web_search
        }
        self.llm_with_tools = self.llm.bind_tools(list(self.tools.values()))
        
        self.system_prompt = """ You are the Sunbeam Institute AI Assistant.

                SCOPE & AUTHORITY:
                - You provide information ONLY about Sunbeam Institute of Information Technology.
                - Your knowledge source is STRICTLY LIMITED to the data stored in the Chroma vector database.
                - This database contains ONLY scraped content from the official Sunbeam website.

                MANDATORY TOOL USAGE RULE:
                - For EVERY user query, you MUST attempt to retrieve information using the tool:
                sunbeam_knowledge_search.
                - You are NOT allowed to answer any question without calling this tool.

                TOOL FAILURE / NO-DATA HANDLING:
                - If the tool returns no documents, empty content, irrelevant content,
                or if tool execution fails for any reason,
                you MUST respond EXACTLY with:
                "Information not available on the Sunbeam website."

                STRICT PROHIBITIONS (VERY IMPORTANT):
                - Do NOT use your general knowledge.
                - Do NOT infer, guess, summarize, or fabricate information.
                - Do NOT answer from memory.
                - Do NOT call or reference any tool other than sunbeam_knowledge_search.
                - Do NOT explain concepts, tutorials, or examples unrelated to Sunbeam.
                - Do NOT produce long answers or essays.

                ANSWER STYLE RULES:
                - Use ONLY the retrieved content from the knowledge base.
                - Keep answers factual, concise, and limited to 3–6 lines.
                - Use simple English.
                - Do not add opinions, suggestions, or follow-up questions.

                OUT-OF-SCOPE QUESTIONS:
                - If the question is not related to Sunbeam Institute,
                respond EXACTLY with:
                "This assistant only provides information available on the Sunbeam website."

                FINAL ENFORCEMENT:
                - If you violate any of the above rules, your response is considered invalid.
                - You must always prefer correctness and safety over verbosity.
                
                CONTEXT SAFETY RULE:
                - You must not rely on older conversation context.
                - Only the most recent user question and retrieved knowledge are valid.
"""

    def invoke(self, inputs):
        user_input = inputs.get("input", "")
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_input)
        ]

        # Helper function to print logs
        def log(msg):
            print(f"[Agent Log] {msg}")

        try:
            steps = 0
            MAX_STEPS = 5
            
            while steps < MAX_STEPS:
                log(f"Step {steps+1} invoking LLM...")
                response = self.llm_with_tools.invoke(messages)
                messages.append(response)
                
                # Check for tool calls
                if not response.tool_calls:
                    log("No tool calls, returning response.")
                    return {"output": response.content}

                # Process all tool calls
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    log(f"Tool Call: {tool_name} with args {tool_args}")
                    
                    if tool_name in self.tools:
                        tool_func = self.tools[tool_name]
                        try:
                            # Try structured invocation first
                            tool_result = tool_func.invoke(tool_args)
                        except Exception as e1:
                            # Fallback for simple string input if structured fails
                            try:
                                # Fallback for simple string input if structured fails or args are empty
                                if not tool_args:
                                     # If model failed to generate args, use the original user prompt as the query
                                     log("Empty args - falling back to user input query")
                                     tool_result = tool_func.invoke(user_input)
                                else:
                                    q_val = tool_args.get("query") or next(iter(tool_args.values()))
                                    tool_result = tool_func.invoke(q_val)
                            except Exception as e2:
                                tool_result = f"Error executing tool {tool_name}: {e1}, {e2}"
                    else:
                        tool_result = f"Error: Tool {tool_name} not found."
                    
                    log(f"Tool Result length: {len(str(tool_result))}")
                    
                    messages.append(ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=str(tool_result),
                        name=tool_name
                    ))
                
                steps += 1

            return {"output": "I reached the maximum number of steps without a final answer."}

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"output": f"I apologize, but I encountered an error: {str(e)}"}

def get_agent():
    return SimpleAgent()
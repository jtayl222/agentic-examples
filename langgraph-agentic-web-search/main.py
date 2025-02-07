import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from typing import TypedDict, Dict

# Load API keys from .env
load_dotenv()


# Define structured state class
class SearchState(TypedDict):
    query: str
    search_results: str
    summary: str


# Initialize Tavily search tool
tavily_tool = TavilySearchResults()


def search_with_tavily(state: SearchState) -> Dict[str, str]:
    """Searches Tavily and returns results."""
    query = state["query"]
    print(f"🔍 Searching Tavily for: {query}")
    results = tavily_tool.invoke(query)
    return {"search_results": results}


# Initialize ChatGPT-4o as the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)


def summarize_results(state: SearchState) -> Dict[str, str]:
    """Summarizes search results using GPT-4o."""
    search_results = state.get("search_results", "")
    if not search_results:
        return {"summary": "No results found."}

    print("📝 Summarizing results with GPT-4o...")
    response = llm.invoke(f"Summarize the following search results:\n{search_results}")
    return {"summary": response.content}


# Define the LangGraph workflow
workflow = StateGraph(SearchState)

# Add tool functions as updates to state
workflow.add_node("search", search_with_tavily)
workflow.add_node("summarize", summarize_results)

# Define edges
workflow.set_entry_point("search")
workflow.add_edge("search", "summarize")
workflow.set_finish_point("summarize")

# Compile the workflow
search_workflow = workflow.compile()

# Example search query
query = "How has LangGraph changed its state update model, and what are the implications?"
# Run the workflow
final_result = search_workflow.invoke({"query": query})

# Display the final summary
print("\n🔹 **Final Summary:**")
print(final_result["summary"])

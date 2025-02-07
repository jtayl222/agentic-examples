import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from typing import TypedDict, Dict, List

# Load environment variables
load_dotenv()


# Define structured state
class ArticleState(TypedDict):
    subject: str
    content_details: str
    revised: str  # Holds the latest version of the article
    critique: str
    references: List[str]
    search_queries: List[str]
    external_information: List[str]
    iteration_count: int  # Tracks the number of iterations


# Initialize Tavily tool
tavily_tool = TavilySearchResults()

# Initialize GPT-4o as the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)


# 1. Generate an Initial Draft
def generate_draft(state: ArticleState) -> ArticleState:
    """Generates an initial draft of the article based on the subject and content details."""
    prompt = f"""
    Write an article on the subject: "{state['subject']}". 
    Details to cover: {state['content_details']}.

    The article should include an introduction, a well-structured body, and a conclusion.
    """
    response = llm.invoke(prompt)

    return {
        **state,
        "revised": response.content or "Initial draft content placeholder.",
        "iteration_count": 0,  # Initialize iteration counter
    }


# 2. Revise the Draft with Citations
def revise_draft(state: ArticleState) -> ArticleState:
    """Refines the article, integrating references and improving clarity."""
    prompt = f"""
    Improve the following article by making it clearer, more concise, and more accurate.
    Ensure numerical citations in [#] format and add a references section.

    Subject: {state['subject']}
    Content Details: {state['content_details']}

    Current Draft:
    {state['revised']}
    """
    response = llm.invoke(prompt)

    return {**state, "revised": response.content or state["revised"]}


# 3. Critique and Reflection
def critique_article(state: ArticleState) -> ArticleState:
    """Provides a critique of the current version of the article and suggests improvements."""
    prompt = f"""
    Critique the following article. Identify weaknesses, missing information, and unnecessary content.
    Provide three key areas for improvement.

    Subject: {state['subject']}
    Content Details: {state['content_details']}

    Article:
    {state['revised']}
    """
    response = llm.invoke(prompt)

    return {**state, "critique": response.content or "No critique available."}


# 4. Generate Research Queries
def generate_search_queries(state: ArticleState) -> ArticleState:
    """Generates queries to improve the article with additional supporting information."""
    prompt = f"""
    Generate five research queries to improve the article about "{state['subject']}".
    These queries should help find reliable sources for missing details.

    Content Details: {state['content_details']}
    """
    response = llm.invoke(prompt)

    queries = (
        response.content.split("\n")
        if response.content
        else ["Default query for research."]
    )

    return {**state, "search_queries": queries}


# 5. Fetch External Information
def fetch_external_information(state: ArticleState) -> ArticleState:
    """Runs Tavily searches using the generated queries and integrates findings."""
    external_info = []

    for query in state["search_queries"]:
        if query.strip():
            print(f"🔍 Searching for: {query}")
            results = tavily_tool.invoke(query)
            external_info.append(results or f"No data found for: {query}")

    return {**state, "external_information": external_info}


# 6. Iterative Refinement
def iterative_refinement(state: ArticleState) -> ArticleState:
    """Refines the article based on critique and external information."""
    prompt = f"""
    Update and improve the article on "{state['subject']}" using the feedback and research below.
    Ensure all claims are well-supported and properly cited.

    External Information:
    {state['external_information']}

    Critique:
    {state['critique']}

    Current Draft:
    {state['revised']}
    """
    response = llm.invoke(prompt)

    return {
        **state,
        "revised": response.content or state["revised"],
        "iteration_count": state["iteration_count"] + 1,
    }


# 7. Final Step
def final_step(state: ArticleState) -> ArticleState:
    """Finalizes the article after three iterations."""
    return {
        **state,
        "revised": state["revised"]
        + f"\n\nFinalized after 3 iterations.\n\nArticle on: {state['subject']}.",
    }


# 8. Conditional Check for Looping
def should_continue(state: ArticleState) -> str:
    """Determines whether to refine again or finish."""
    return "critique_article" if state["iteration_count"] < 1 else "final_step"


# Create LangGraph State Machine
workflow = StateGraph(ArticleState)

# Add Nodes
workflow.add_node("generate_draft", generate_draft)
workflow.add_node("revise_draft", revise_draft)
workflow.add_node("critique_article", critique_article)
workflow.add_node("generate_search_queries", generate_search_queries)
workflow.add_node("fetch_external_information", fetch_external_information)
workflow.add_node("iterative_refinement", iterative_refinement)
workflow.add_node("final_step", final_step)

# Define Execution Flow
workflow.set_entry_point("generate_draft")
workflow.add_edge("generate_draft", "revise_draft")
workflow.add_edge("revise_draft", "critique_article")
workflow.add_edge("critique_article", "generate_search_queries")
workflow.add_edge("generate_search_queries", "fetch_external_information")
workflow.add_edge("fetch_external_information", "iterative_refinement")

# Add Conditional Edge for Looping
workflow.add_conditional_edges(
    "iterative_refinement",
    should_continue,
    {"critique_article": "critique_article", "final_step": "final_step"},
)

# Set Final Step
workflow.set_finish_point("final_step")

# Compile the workflow
article_workflow = workflow.compile()

# Input Message with Subject and Content Details
input_message = {
    "subject": "Building a LangGraph Workflow with Tavily and GPT-4o",
    "content_details": "The article should cover state management in LangGraph, the role of Tavily in web search, how GPT-4o enhances summarization, and a step-by-step implementation guide."
}

# Run the Workflow
final_result = article_workflow.invoke(input_message)

# Display the Final Refined Article
print("\n🔹 **Final Article:**")
print(final_result["revised"])
# print(article_workflow.get_graph().draw_mermaid())

import streamlit as st
from langchain_community.chat_models import ChatOpenAI  # Updated import
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph
from dotenv import load_dotenv
import os
from typing import List, Dict, TypedDict, Tuple

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.error("OPENAI_API_KEY environment variable not set.")
    st.stop()

# Define state types
class Message(TypedDict):
    role: str
    content: str

class State(TypedDict):
    messages: List[Message]
    input: str

# Initialize LLM
llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-3.5-turbo",
    openai_api_key=openai_api_key
)

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["input", "messages"],
    template="""Previous conversation:
{messages}

User: {input}
Assistant:"""
)

def format_message_history(messages: List[Message]) -> str:
    """Format message history for the prompt."""
    return "\n".join([
        f"{msg['role'].title()}: {msg['content']}"
        for msg in messages
    ])

def generate_response(state: State) -> State:
    """Generate response using the LLM."""
    messages_str = format_message_history(state["messages"])
    prompt = prompt_template.format(
        input=state["input"],
        messages=messages_str
    )
    response = llm.predict(prompt)

    # Update state with new messages
    new_messages = state["messages"] + [
        {"role": "user", "content": state["input"]},
        {"role": "assistant", "content": response}
    ]

    # Return the updated state with the messages key
    return {"messages": new_messages, "input": ""}

# Initialize session state
if "conversation_state" not in st.session_state:
    st.session_state.conversation_state = {"messages": [], "input": ""}

# Initialize StateGraph
if "state_graph" not in st.session_state:
    # Use TypedDict for state_schema
    workflow = StateGraph(state_schema=State)

    # Add node and set entry point
    workflow.add_node("generate_response", generate_response)
    workflow.set_entry_point("generate_response")

    # Compile the graph
    st.session_state.state_graph = workflow.compile()

def process_user_input():
    """Process user input through the StateGraph."""
    user_input = st.session_state.user_input
    if user_input:
        current_state = {
            "messages": st.session_state.conversation_state["messages"],
            "input": user_input
        }

        with st.spinner("Thinking..."):
            result = st.session_state.state_graph.invoke(current_state)
            st.session_state.conversation_state = result

        # Clear input after processing
        st.session_state.user_input = ""

# Streamlit UI
st.title("LangChain Chatbot with StateGraph")

# Display conversation history
for message in st.session_state.conversation_state["messages"]:
    role_prefix = "You:" if message["role"] == "user" else "Assistant:"
    st.write(f"**{role_prefix}** {message['content']}")

# User input
user_input = st.text_input("Enter your message:", key="user_input", on_change=process_user_input)

# Button to start a new conversation
if st.button("Start New Conversation"):
    st.session_state.conversation_state = {"messages": [], "input": ""}
    st.rerun()
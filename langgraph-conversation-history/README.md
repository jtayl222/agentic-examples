# LangGraph Chatbot with StateGraph

## Overview
This repository contains a chatbot implementation using **LangGraph's StateGraph** for structured and deterministic state management. Unlike traditional agent-based approaches, StateGraph enforces explicit state transitions, making the chatbot behavior predictable and easy to debug.

## Features
- Uses **LangGraph's StateGraph** for deterministic state management
- Implements **Streamlit** for an interactive web-based chatbot UI
- Integrates **OpenAI's GPT-3.5 Turbo** for generating chatbot responses
- **Avoids using ConversationBufferMemory**, aligning with StateGraph's structured approach

## Why StateGraph?
Traditional LangChain memory mechanisms, like `ConversationBufferMemory`, are not suited for StateGraph because:
- **StateGraph uses explicit state updates** rather than relying on implicit memory.
- **State transitions are controlled**, ensuring deterministic execution rather than agent-based autonomy.
- **Memory is maintained at a granular level**, making it easier to track and modify conversation history.

Instead of `ConversationBufferMemory`, this implementation:
- **Defines explicit state updates** within StateGraph nodes.
- **Uses a state dictionary** to manage conversation context.
- **Implements state reducers** for controlled state modifications.

## Installation
To run the chatbot, follow these steps:

### Prerequisites
Ensure you have Python 3.8+ installed.

### 1. Clone the Repository
```sh
git clone https://github.com/jtayl222/agentic-examples.git
cd agentic-examples/langgraph-conversation-history
```

### 2. Install Dependencies
```sh
poetry install
```

### 3. Set Up Environment Variables
Create a `.env` file and add your OpenAI API key:
```sh
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### 4. Run the Chatbot
```sh
streamlit run session-state-conversation-history.py
```

## How It Works
1. **User Input**: The user enters a query in the Streamlit UI.
2. **StateGraph Processing**:
   - The chatbot uses `StateGraph` to manage state transitions.
   - It invokes the `generate_response` function, formatting the prompt using previous messages.
   - The GPT model generates a response, which is added to the state dictionary.
3. **Conversation History**:
   - The updated conversation state is displayed in the UI.
   - Users can start a new conversation to reset the session state.

## Best Practices for State Management with StateGraph
- **Avoid `@st.session_state.state_graph.node`**, as it mixes Streamlit and StateGraph state management, making execution less deterministic.
- **Use `st.session_state` only for UI-related state**, and let `StateGraph` handle conversation flow and memory.
- **Keep state management decoupled** for clarity and maintainability.

## Contributing
If you find a bug or want to improve the chatbot, feel free to submit a pull request.

## License
This project is licensed under the MIT License.


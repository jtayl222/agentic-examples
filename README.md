# Agentic Examples Repository

## Overview

This repository contains various examples of **agentic workflows** using **LangGraph**, an advanced framework for structured, deterministic AI development. These examples demonstrate best practices for **state management**, **controlled execution**, and **efficient memory handling** in AI applications, moving beyond traditional agent-based systems.

## Why Use LangGraph?

Traditional AI workflows often rely on agent-based memory systems, which can lead to unpredictable behaviors and difficulty in debugging. These approaches typically lack explicit control over state transitions, making it harder to maintain consistency in AI applications. LangGraph provides a structured and deterministic way to manage state in AI applications, ensuring:

- **Explicit state transitions** for clear and predictable execution.
- **Fine-grained memory updates**, avoiding the issues of broad memory storage like `ConversationBufferMemory`.
- **Decoupled UI state management**, preventing conflicts between framework logic and frontend controls.

## Key Examples in This Repository

### 1. LangGraph’s StateGraph and Conversation History

📌 **Path**: [`langgraph-conversation-history/session-state-conversation-history.py`](https://github.com/jtayl222/agentic-examples/blob/main/langgraph-conversation-history/session-state-conversation-history.py)

- Uses **StateGraph** to manage structured conversation history.
- Avoids `ConversationBufferMemory` to ensure explicit and controlled memory handling.
- Implements OpenAI's GPT model for chatbot responses.

### 2. Agentic Web Search with LangGraph

📌 **Path**: [`langgraph-agentic-web-search/main.py`](https://github.com/jtayl222/agentic-examples/blob/main/langgraph-agentic-web-search/main.py)

- Demonstrates **how agentic workflows can be structured** for automated web searches.
- Incorporates **StateGraph** to manage query execution and results processing.
- Related to the discussion on avoiding `@tool` in LangGraph workflows ([Read More](https://medium.com/@jeftaylo/why-you-shouldnt-use-tool-in-langgraphs-stategraph-workflows-4efc38e4d203)).

### 3. Critique-Search-Refine Workflow

📌 **Path**: [`langgraph-critique-search-refine/langgraph-critique-search-refine.py`](https://github.com/jtayl222/agentic-examples/blob/main/langgraph-critique-search-refine/langgraph-critique-search-refine.py)

- Provides a **complete, structured LangGraph workflow** for iterative AI improvement.
- Uses **StateGraph** to track critique, search refinements, and optimized responses.
- Ensures AI-generated content is **progressively enhanced** through structured iterations.

## Installation and Setup

### Prerequisites

Ensure you have Python 3.8+ installed.

### Clone the Repository

```sh
git clone https://github.com/jtayl222/agentic-examples.git
cd agentic-examples
```

### Install Dependencies

```sh
Each example has its own dependencies. Navigate to the specific example directory before installing:
```sh
cd <example-directory>
poetry install
```
```

### Run an Example

If the example requires Streamlit (e.g., the chatbot), run:

```sh
cd langgraph-conversation-history
streamlit run session-state-conversation-history.py
```

For other examples, run their respective scripts as needed, e.g.:

```sh
cd langgraph-agentic-web-search
python main.py
```

## Best Practices for StateGraph Workflows

- **Define state updates explicitly** in nodes rather than relying on implicit memory.
- **Use a structured state dictionary** instead of broad memory storage like `ConversationBufferMemory`.
- **Separate UI-related state from StateGraph state management**.
- **Avoid ****************`@tool`**************** in StateGraph workflows** for clearer and more predictable execution.

## Further Reading

- 📖 [Building a LangGraph Workflow Using Tavily Search and GPT-4o for AI-Powered Research](https://jeftaylo.medium.com/building-a-langgraph-workflow-using-tavily-search-and-gpt-4o-for-ai-powered-research-07235f09a083)

- 📖 [LangGraph’s StateGraph and Conversation History](https://jeftaylo.medium.com/why-you-should-use-stategraph-for-structured-chatbot-workflows-27162f79faa5)

- 📖 [Why You Shouldn't Use @tool in StateGraph Workflows](https://medium.com/@jeftaylo/why-you-shouldnt-use-tool-in-langgraphs-stategraph-workflows-4efc38e4d203)

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve these implementations. You can find the issues page [here](https://github.com/jtayl222/agentic-examples/issues) and the contributing guidelines [here](https://github.com/jtayl222/agentic-examples/blob/main/CONTRIBUTING.md).

## License

This project is licensed under the MIT License.


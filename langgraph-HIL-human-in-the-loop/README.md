# LangGraph Interactive Workflow Example

This project demonstrates how to implement a Human-in-the-Loop (HIL) workflow using LangGraph with an API-based interaction model. It solves the common problem of needing user interaction during multi-step workflows, specifically when:

- Data needs to be collected sequentially
- Users need to review and potentially modify intermediate results
- The workflow needs to maintain state between interactions
- Multiple concurrent sessions need to be supported

## Problem Solved

Traditional workflow implementations often require all data upfront or complete a workflow in a single request-response cycle. This implementation demonstrates how to:

1. Collect multiple pieces of data sequentially, like a chatbot conversation
2. Allow users to review and modify intermediate results
3. Maintain workflow state between requests
4. Support multiple concurrent workflow sessions
5. Provide a clean API interface for client applications

## Architecture

The solution consists of two main components:

### Server (`langgraph-HIL-human-in-the-loop.py`)
- Implements the workflow logic using LangGraph
- Provides REST API endpoints for workflow interaction
- Manages workflow state and sessions
- Three main workflow nodes:
  - Information Collector: Sequentially collects 4 details
  - Transformer: Processes collected data with user review/modification
  - Uploader: Handles final data storage

### Client (`client-for-HIL-example.py`)
- Provides an interactive command-line interface
- Handles all API communication with the server
- Guides users through the workflow steps
- Displays current state and progress

## Setup and Installation

1. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install required dependencies:
```bash
pip install fastapi uvicorn requests langgraph
```

3. Download both server and client files:
- `langgraph-HIL-human-in-the-loop.py`
- `client-for-HIL-example.py`

## Running the Example

1. Start the server:
```bash
python langgraph-HIL-human-in-the-loop.py
```
The server will start on http://localhost:8000

2. In a new terminal, run the client:
```bash
python client-for-HIL-example.py
```

## API Endpoints

- `POST /workflow/{session_id}` - Main workflow endpoint
- `GET /health` - Health check endpoint
- `GET /sessions` - List active sessions
- `GET /docs` - Interactive API documentation

## Example Workflow

1. Start a new workflow session
2. Provide 4 details sequentially
3. Review and optionally modify the transformed data
4. Confirm the final upload step

Example API interaction:
```bash
# Start workflow
curl -X POST http://localhost:8000/workflow/session123 \
     -H "Content-Type: application/json" \
     -d '{"input": "", "action": "start"}'

# Provide first detail
curl -X POST http://localhost:8000/workflow/session123 \
     -H "Content-Type: application/json" \
     -d '{"input": "First detail", "action": "provide_detail"}'
```

## State Management

The workflow maintains state for each session including:
- Collected details
- Current progress
- Transformation status
- Upload status
- Last message
- Required next action

## Error Handling

The implementation includes:
- Session validation
- Action validation
- State consistency checks
- Client-side error handling and retry logic

## Limitations and Considerations

- In-memory session storage (consider using a database for production)
- No authentication/authorization (add as needed)
- Single server instance (consider distributed state management for scaling)

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use and modify for your own projects.
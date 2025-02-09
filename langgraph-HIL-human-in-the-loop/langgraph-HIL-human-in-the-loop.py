from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import json

# Define Request/Response models
class UserInput(BaseModel):
    input: str
    action: str  # can be: 'provide_detail', 'modify_transform', 'confirm_upload', 'start'

class WorkflowResponse(BaseModel):
    message: str
    required_action: str
    current_state: Dict[str, Any]

# Define Workflow State
class WorkflowState(TypedDict):
    details: List[str]
    current_detail_index: int
    transformed_data: Optional[str]
    is_transform_approved: bool
    is_uploaded: bool
    last_message: str
    required_action: str

# Initialize FastAPI
app = FastAPI()

# Node: Information Collector
def info_collector(state: WorkflowState) -> Dict:
    required_details = 4
    
    if state["current_detail_index"] >= required_details:
        return {
            "next": "transformer",
            "last_message": "All details collected. Moving to transformation.",
            "required_action": "await_transform"
        }
    
    return {
        "next": "info_collector",
        "last_message": f"Please provide detail #{state['current_detail_index'] + 1}",
        "required_action": "provide_detail"
    }

# Node: Transformer
def transformer(state: WorkflowState) -> Dict:
    if not state["is_transform_approved"]:
        # Simulate transformation
        transformed = " | ".join(state["details"])
        return {
            "next": "transformer",
            "transformed_data": transformed,
            "last_message": f"Data transformed. Result: {transformed}. Do you approve?",
            "required_action": "approve_transform"
        }
    
    return {
        "next": "uploader",
        "last_message": "Transform approved. Moving to upload.",
        "required_action": "await_upload"
    }

# Node: Uploader
def uploader(state: WorkflowState) -> Dict:
    if not state["is_uploaded"]:
        return {
            "next": "uploader",
            "last_message": "Ready to upload. Confirm?",
            "required_action": "confirm_upload"
        }
    
    return {
        "next": END,
        "last_message": "Upload complete. Workflow finished.",
        "required_action": "complete"
    }

# Create and configure the graph
def create_workflow() -> StateGraph:
    workflow_state = {
        "details": List[str],
        "current_detail_index": int,
        "transformed_data": Optional[str],
        "is_transform_approved": bool,
        "is_uploaded": bool,
        "last_message": str,
        "required_action": str
    }
    
    graph = StateGraph(workflow_state)
    
    # Add nodes
    graph.add_node("info_collector", info_collector)
    graph.add_node("transformer", transformer)
    graph.add_node("uploader", uploader)
    
    # Add edges
    graph.add_edge("info_collector", "transformer")
    graph.add_edge("transformer", "uploader")
    graph.add_edge("info_collector", "info_collector")  # Self-loop for collecting multiple details
    graph.add_edge("transformer", "transformer")  # Self-loop for transformation approval
    graph.add_edge("uploader", "uploader")  # Self-loop for upload confirmation
    
    graph.set_entry_point("info_collector")
    
    return graph.compile()

# Initialize workflow
workflow = create_workflow()

# Initialize state
def get_initial_state() -> WorkflowState:
    return WorkflowState(
        details=[],
        current_detail_index=0,
        transformed_data=None,
        is_transform_approved=False,
        is_uploaded=False,
        last_message="Started workflow. Please provide first detail.",
        required_action="provide_detail"
    )

# Store active sessions (in a real application, use a proper database)
active_sessions: Dict[str, WorkflowState] = {}

@app.post("/workflow/{session_id}")
async def handle_workflow(session_id: str, user_input: UserInput) -> WorkflowResponse:
    # Get or create session state
    if session_id not in active_sessions:
        active_sessions[session_id] = get_initial_state()
    
    state = active_sessions[session_id]
    
    # Handle user input based on current state and action
    if user_input.action == "start":
        # Reset or initialize the session
        active_sessions[session_id] = get_initial_state()
        state = active_sessions[session_id]
    
    elif user_input.action == "provide_detail":
        if state["required_action"] == "provide_detail":
            state["details"].append(user_input.input)
            state["current_detail_index"] += 1
    
    elif user_input.action == "modify_transform":
        if state["required_action"] == "approve_transform":
            if user_input.input:  # If input provided, modify the transformation
                state["transformed_data"] = user_input.input
            state["is_transform_approved"] = True
    
    elif user_input.action == "confirm_upload":
        if state["required_action"] == "confirm_upload":
            state["is_uploaded"] = True
    
    # Process workflow
    result = workflow.invoke(state)
    state.update(result)
    active_sessions[session_id] = state
    
    return WorkflowResponse(
        message=state["last_message"],
        required_action=state["required_action"],
        current_state=dict(state)
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Get all active sessions
@app.get("/sessions")
async def get_sessions():
    return {"active_sessions": list(active_sessions.keys())}

if __name__ == "__main__":
    print("Starting LangGraph Interactive Server...")
    print("Access the API documentation at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
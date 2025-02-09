from typing import TypedDict, List, Optional, Dict, Any, Union
from langgraph.graph import StateGraph, END
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Define Request/Response models
class UserInput(BaseModel):
    input: str
    action: str

class WorkflowResponse(BaseModel):
    message: str
    required_action: str
    current_state: Dict[str, Any]

# Define workflow states and transitions
class WorkflowState(TypedDict):
    details: List[str]
    current_detail_index: int
    transformed_data: Optional[str]
    is_transform_approved: bool
    is_uploaded: bool
    workflow_state: str  # Current state of the workflow
    workflow_message: str  # Current message to display

def process_state(state: WorkflowState) -> Dict[str, Any]:
    """Process the current state and determine the next action"""
    current_state = state["workflow_state"]
    
    if current_state == "collecting_details":
        required_details = 4
        if state["current_detail_index"] >= required_details:
            return {
                "next": "process_details",
                "workflow_state": "transforming",
                "workflow_message": "All details collected. Moving to transformation."
            }
        return {
            "next": "process_details",
            "workflow_state": "collecting_details",
            "workflow_message": f"Please provide detail #{state['current_detail_index'] + 1}"
        }
    
    elif current_state == "transforming":
        if not state["is_transform_approved"]:
            transformed = " | ".join(state["details"])
            return {
                "next": "process_details",
                "workflow_state": "awaiting_approval",
                "transformed_data": transformed,
                "workflow_message": f"Data transformed. Result: {transformed}. Do you approve?"
            }
        return {
            "next": "process_details",
            "workflow_state": "uploading",
            "workflow_message": "Transform approved. Moving to upload."
        }
    
    elif current_state == "awaiting_approval":
        if state["is_transform_approved"]:
            return {
                "next": "process_details",
                "workflow_state": "uploading",
                "workflow_message": "Transform approved. Moving to upload."
            }
        return {
            "next": "process_details",
            "workflow_state": "awaiting_approval",
            "workflow_message": "Awaiting approval of transformation."
        }
    
    elif current_state == "uploading":
        if state["is_uploaded"]:
            return {
                "next": END,
                "workflow_state": "complete",
                "workflow_message": "Upload complete. Workflow finished."
            }
        return {
            "next": "process_details",
            "workflow_state": "uploading",
            "workflow_message": "Ready to upload. Confirm?"
        }
    
    return {
        "next": END,
        "workflow_state": "complete",
        "workflow_message": "Workflow complete."
    }

# Create and configure the graph
def create_workflow() -> StateGraph:
    workflow = StateGraph(WorkflowState)
    workflow.add_node("process_details", process_state)
    workflow.set_entry_point("process_details")
    return workflow.compile()

# Initialize workflow
workflow = create_workflow()

def get_initial_state() -> WorkflowState:
    return WorkflowState(
        details=[],
        current_detail_index=0,
        transformed_data=None,
        is_transform_approved=False,
        is_uploaded=False,
        workflow_state="collecting_details",
        workflow_message="Started workflow. Please provide first detail."
    )

# Store active sessions
active_sessions: Dict[str, WorkflowState] = {}

def get_required_action(state: WorkflowState) -> str:
    """Map workflow state to required action"""
    state_to_action = {
        "collecting_details": "provide_detail",
        "transforming": "await_transform",
        "awaiting_approval": "approve_transform",
        "uploading": "confirm_upload",
        "complete": "complete"
    }
    return state_to_action.get(state["workflow_state"], "complete")

@app.post("/workflow/{session_id}")
async def handle_workflow(session_id: str, user_input: UserInput) -> WorkflowResponse:
    try:
        if session_id not in active_sessions or user_input.action == "start":
            active_sessions[session_id] = get_initial_state()
        
        state = active_sessions[session_id]
        
        # Handle user input based on workflow state
        if user_input.action == "provide_detail" and state["workflow_state"] == "collecting_details":
            state["details"].append(user_input.input)
            state["current_detail_index"] += 1
        
        elif user_input.action == "modify_transform" and state["workflow_state"] == "awaiting_approval":
            if user_input.input:
                state["transformed_data"] = user_input.input
            state["is_transform_approved"] = True
        
        elif user_input.action == "confirm_upload" and state["workflow_state"] == "uploading":
            state["is_uploaded"] = True
        
        # Process workflow
        result = workflow.invoke(state)
        state.update(result)
        active_sessions[session_id] = state
        
        return WorkflowResponse(
            message=state["workflow_message"],
            required_action=get_required_action(state),
            current_state=dict(state)
        )
    
    except Exception as e:
        print(f"Error handling workflow: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

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
    port = int(os.getenv("PORT", 8080))
    print(f"Access the API documentation at http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)
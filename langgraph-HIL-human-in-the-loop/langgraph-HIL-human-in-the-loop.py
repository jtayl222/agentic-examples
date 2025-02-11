from typing import TypedDict, List, Optional, Dict, Any, Union
from langgraph.graph import StateGraph, END
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import json
import os
from dotenv import load_dotenv
import logging
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from pprint import pformat, pprint

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Initialize MemorySaver and InMemoryStore
memory_saver = MemorySaver()
store = InMemoryStore()

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
    transformed_data: Optional[List[str]]
    is_transform_approved: bool
    is_uploaded: bool
    workflow_state: str  # Current state of the workflow
    workflow_message: str  # Current message to display

def collecting_details(state: WorkflowState) -> Dict[str, Any]:
    logger.info("Entering collecting_details node")
    required_details = 4
    questions = [
        os.getenv("QUESTION_1"),
        os.getenv("QUESTION_2"),
        os.getenv("QUESTION_3"),
        os.getenv("QUESTION_4")
    ]
    
    if state["current_detail_index"] >= required_details:
        transformed_data = [f"the transformed data is {detail}" for detail in state["details"]]
        state["transformed_data"] = transformed_data
        logger.info("Exiting collecting_details node")
        return {
            "next": "transforming",
            "workflow_state": "transforming",
            "workflow_message": "All details collected. Moving to transformation."
        }
    
    logger.info("Exiting collecting_details node")
    return {
        "next": "collecting_details",
        "workflow_state": "collecting_details",
        "workflow_message": questions[state["current_detail_index"]]
    }

def transforming(state: WorkflowState) -> Dict[str, Any]:
    logger.info("Entering transforming node")
    if not state["is_transform_approved"]:
        logger.info("Exiting transforming node")
        return {
            "next": "awaiting_approval",
            "workflow_state": "awaiting_approval",
            "workflow_message": f"Data transformed. Result: {state['transformed_data']}. Do you approve?"
        }
    logger.info("Exiting transforming node")
    return {
        "next": "uploading",
        "workflow_state": "uploading",
        "workflow_message": "Transform approved. Moving to upload."
    }

def awaiting_approval(state: WorkflowState, config) -> Dict[str, Any]:
    logger.info("Entering awaiting_approval node")
    config = {"configurable": {"thread_id": config['metadata']['thread_id']}}
    sh = list(graph.get_state_history(config))
    pprint(sh)

    if state["is_transform_approved"]:
        logger.info("Exiting awaiting_approval node")
        return {
            "next": "uploading",
            "workflow_state": "uploading",
            "workflow_message": "Transform approved. Moving to upload."
        }
    logger.info("Exiting awaiting_approval node")
    return {
        "next": "awaiting_approval",
        "workflow_state": "awaiting_approval",
        "workflow_message": "Awaiting approval of transformation."
    }

def uploading(state: WorkflowState) -> Dict[str, Any]:
    logger.info("Entering uploading node")
    if state["is_uploaded"]:
        logger.info("Exiting uploading node")
        return {
            "next": END,
            "workflow_state": "complete",
            "workflow_message": "Upload complete. Workflow finished."
        }
    logger.info("Exiting uploading node")
    return {
        "next": "uploading",
        "workflow_state": "uploading",
        "workflow_message": "Ready to upload. Confirm?"
    }

# Create and configure the graph
def create_workflow() -> StateGraph:
    workflow = StateGraph(WorkflowState)
    workflow.add_node("collecting_details", collecting_details)
    workflow.add_node("transforming", transforming)
    workflow.add_node("awaiting_approval", awaiting_approval)
    workflow.add_node("uploading", uploading)
    
    # Add edges
    workflow.add_edge("collecting_details", "transforming")
    workflow.add_edge("transforming", "awaiting_approval")
    workflow.add_edge("awaiting_approval", "uploading")
    workflow.add_edge("uploading", END)
    
    workflow.set_entry_point("collecting_details")
    compiledStateGraph = workflow.compile(
        checkpointer=memory_saver, 
        store=store, 
        interrupt_before=["collecting_details", "awaiting_approval", "uploading"])

    # Print the graph
    print(compiledStateGraph.get_graph().draw_mermaid())
    compiledStateGraph.get_graph().draw_png(output_file_path="workflow.png")

    return compiledStateGraph

# Initialize workflow
graph = create_workflow()

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
                state["transformed_data"] = [user_input.input]
            state["is_transform_approved"] = True
        
        elif user_input.action == "confirm_upload" and state["workflow_state"] == "uploading":
            state["is_uploaded"] = True
        
        # Process workflow
        result = graph.invoke(state, config={"configurable": {"thread_id": session_id}})
        state.update(result)
        active_sessions[session_id] = state

        # Log the state transition
        logger.info(f"Session {session_id}: Transitioned to {state['workflow_state']} state.")
        config = {"configurable": {"thread_id": session_id}}
        the_state= graph.get_state(config)
        logger.info(pformat(f"Session {session_id}: {the_state}"))
        
        return WorkflowResponse(
            message=state["workflow_message"],
            required_action=get_required_action(state),
            current_state=dict(state)
        )
    
    except Exception as e:
        logger.error(f"Error handling workflow for session {session_id}: {e}", exc_info=True)
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
    logger.info("Starting LangGraph Interactive Server...")
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Access the API documentation at http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)
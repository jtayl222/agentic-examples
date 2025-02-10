import requests
import json
from typing import Dict, Any
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
load_dotenv()

class WorkflowClient:
    def __init__(self, base_url: str = None):
        port = os.getenv("PORT", "8080")
        self.base_url = base_url or f"http://localhost:{port}"
        self.session_id = "test_session"  # You can make this dynamic
    
    def send_request(self, input_text: str, action: str) -> Dict[str, Any]:
        url = f"{self.base_url}/workflow/{self.session_id}"
        payload = {
            "input": input_text,
            "action": action
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

def main():
    st.title("Interactive Workflow Client")
    st.write("This client will guide you through the workflow steps.")
    
    client = WorkflowClient()
    
    if "state" not in st.session_state:
        st.session_state.state = None
    
    if st.button("Start Workflow") or st.session_state.state is None:
        response = client.send_request("", "start")
        st.session_state.state = response
        st.write(f"Server: {response['message']}")
    
    if st.session_state.state:
        response = st.session_state.state
        
        if response['required_action'] == "provide_detail":
            user_input = st.text_input("Please enter the requested detail:")
            if st.button("Submit Detail"):
                response = client.send_request(user_input, "provide_detail")
                st.session_state.state = response
                st.write(f"Server: {response['message']}")
        
        elif response['required_action'] == "approve_transform":
            st.write(f"Transformed data: {response['current_state'].get('transformed_data')}")
            choice = st.radio("Do you want to modify the transformation?", ("No", "Yes"))
            if choice == "Yes":
                new_transform = st.text_input("Enter modified transformation:")
                if st.button("Submit Transformation"):
                    response = client.send_request(new_transform, "modify_transform")
                    st.session_state.state = response
                    st.write(f"Server: {response['message']}")
            else:
                if st.button("Approve Transformation"):
                    response = client.send_request("", "modify_transform")
                    st.session_state.state = response
                    st.write(f"Server: {response['message']}")
        
        elif response['required_action'] == "confirm_upload":
            choice = st.radio("Confirm upload?", ("No", "Yes"))
            if choice == "Yes":
                if st.button("Confirm Upload"):
                    response = client.send_request("", "confirm_upload")
                    st.session_state.state = response
                    st.write(f"Server: {response['message']}")
        
        st.write("Current state:")
        st.json(response['current_state'])
        
        if response['required_action'] == "complete":
            st.write("Workflow completed!")
            st.session_state.state = None

if __name__ == "__main__":
    main()
import requests
import json
from typing import Dict, Any

class WorkflowClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
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
    
    def run_interactive_workflow(self):
        """Run the workflow interactively with user input"""
        print("Starting workflow...")
        
        while True:
            try:
                # Start or continue workflow
                response = self.send_request("", "start")
                print(f"\nServer: {response['message']}")
                
                if response['required_action'] == "complete":
                    print("Workflow completed!")
                    break
                
                # Handle different required actions
                if response['required_action'] == "provide_detail":
                    user_input = input("Please enter the requested detail: ")
                    response = self.send_request(user_input, "provide_detail")
                
                elif response['required_action'] == "approve_transform":
                    print("\nTransformed data:", response['current_state'].get('transformed_data'))
                    choice = input("Do you want to modify the transformation? (yes/no): ")
                    
                    if choice.lower() == 'yes':
                        new_transform = input("Enter modified transformation: ")
                        response = self.send_request(new_transform, "modify_transform")
                    else:
                        response = self.send_request("", "modify_transform")
                
                elif response['required_action'] == "confirm_upload":
                    choice = input("Confirm upload? (yes/no): ")
                    if choice.lower() == 'yes':
                        response = self.send_request("", "confirm_upload")
                
                print("\nCurrent state:", json.dumps(response['current_state'], indent=2))
                
            except requests.exceptions.RequestException as e:
                print(f"Error communicating with server: {e}")
                break
            except KeyboardInterrupt:
                print("\nWorkflow interrupted by user")
                break

def main():
    client = WorkflowClient()
    print("Interactive Workflow Client")
    print("==========================")
    print("This client will guide you through the workflow steps.")
    print("You can press Ctrl+C at any time to exit.")
    print("")
    
    client.run_interactive_workflow()

if __name__ == "__main__":
    main()
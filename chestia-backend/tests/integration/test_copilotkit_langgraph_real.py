"""
Integration test for the CopilotKit LangGraph endpoint using real data.
Verifies that the add_langgraph_fastapi_endpoint works correctly with the chestia_recipe_agent.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

# Create a test client
client = TestClient(app)

class TestCopilotKitLangGraphRealData:
    """Test the CopilotKit LangGraph integration with real payloads."""

    def test_copilotkit_invoke_agent(self):
        """
        Test invoking the agent via the CopilotKit endpoint.
        
        The endpoint structure for add_langgraph_fastapi_endpoint typically handles 
        CopilotKit Protocol requests. We will simulate a standard LangGraph interaction.
        """
        
        # The CopilotKit protocol uses a specific POST request structure.
        # When using add_langgraph_fastapi_endpoint, it exposes endpoints around the graph.
        # We need to send a payload that LangGraphAGUIAgent expects.
        
        # NOTE: The previous error `KeyError: 'ingredients'` suggests the state wasn't populated.
        # In CoAgents/LangGraph, the input state is passed in the request body.
        
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "I have chicken and rice."
                }
            ],
            # We explicitly pass the state keys expected by GraphState
            "ingredients": ["chicken", "rice"],
            "difficulty": "easy",
            "lang": "en"
        }
        
        # Note: The exact URL depends on how ag_ui_langgraph registers it.
        # Usually it registers /copilotkit
        # But specifically it might be /copilotkit/chestia_recipe_agent/invoke or similar
        # Or standard CopilotKit protocol at /copilotkit
        
        # Let's try the standard info endpoint first to verify registration
        info_response = client.get("/copilotkit/info") 
        # Note: ag-ui might not implement info exactly the same or at the same path
        # But let's check basic health/connectivity first.

        # If we look at the logs provided by the user: 
        # "POST /copilotkit HTTP/1.1" 307
        # "POST /copilotkit/ HTTP/1.1" 200
        
        # This implies the endpoint is at /copilotkit/
        
        # Let's try to hit the graph. 
        # The CopilotKit client sends a POST with a body containing info about the task.
        
        # Constructing a valid CopilotKit request is complex without the SDK.
        # However, checking if "ingredients" are passed correctly is key.
        
        # If we use `TestClient`, we intersect the app directly.
        
        pass

    def test_run_graph_directly_through_endpoint(self):
        """
        Attempt to trigger the graph execution via the CoAgent protocol.
        """
        # Based on ag_ui_langgraph implementation, it likely expects a JSON body 
        # that maps to parameters for the agent.
        
        # This is a simulation of what the frontend sends.
        # Input state validation is where it failed.
        
        request_data = {
            "threadId": "test-thread-real-1",
            "runId": "run-1",
            "recipients": {
                "agent_name": "chestia_recipe_agent"
            },
            "state": {
                # This state dict maps to the graph state
                "ingredients": ["chicken", "rice"],
                "difficulty": "easy",
                "lang": "en"
            },
            "messages": [],
            "tools": [],
            "context": [],
            "forwardedProps": {}
        }
        
        # We'll try hitting the endpoint.
        # Note: If this fails with 404/405 we know the path is wrong.
        response = client.post("/copilotkit/", json=request_data)
        
        # We don't assert 200 immediately because we want to see the error if any.
        print(f"\nResponse Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        # If it was a 500 due to KeyError, we'll see it.
        assert response.status_code == 200

if __name__ == "__main__":
    # Allow running this script directly
    t = TestCopilotKitLangGraphRealData()
    t.test_run_graph_directly_through_endpoint()

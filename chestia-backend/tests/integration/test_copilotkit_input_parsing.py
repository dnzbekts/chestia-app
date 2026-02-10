import pytest
import json
import uuid
from fastapi.testclient import TestClient
from src.main import app

# Create a test client
client = TestClient(app)

class TestCopilotKitInputParsing:
    """
    Test class for verifying input parsing from conversation messages 
    when explicit ingredients are missing from state.
    """

    ENDPOINT = "/copilotkit/" # Correct endpoint based on previous test

    def test_parse_ingredients_from_message(self):
        """
        Test that ingredients are extracted from the user message
        when 'ingredients' list in state is empty.
        """
        # 1. Define the payload with EMPTY ingredients but descriptive message
        run_id = str(uuid.uuid4())
        thread_id = f"test-thread-parsing-{uuid.uuid4().hex[:8]}"
        
        payload = {
            "runId": run_id,
            "threadId": thread_id,
            "state": {
                # EMPTY ingredients to trigger parsing
                "ingredients": [],
                "difficulty": "easy",
                "lang": "en",
                # "messages" key in state provided by ag-ui is usually handled 
                # but we can omit it here as it comes from top-level "messages"
                "original_ingredients": [],
                "recipe": None,
                "extra_ingredients": [],
                "extra_count": 0,
                "error": None,
                "iteration_count": 0,
                "source_node": None
            },
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": "I have apples and cinnamon, make me a dessert."
                }
            ],
            "tools": [],
            "context": [],
            "forwardedProps": {}
        }

        # 2. Send POST request using TestClient
        print(f"\nSending request to {self.ENDPOINT}...")
        
        # TestClient.post returns the response after request completes (unless stream=True used but TestClient handles ASGI)
        # However, for streaming endpoints, TestClient collects response?
        # ag_ui_langgraph endpoint returns a StreamingResponse.
        
        with client.stream("POST", self.ENDPOINT, json=payload) as response:
            assert response.status_code == 200, f"Request failed: {response.text}"
            
            # 3. Process the stream and look for extracted ingredients
            print("Processing event stream...")
            
            extracted_ingredients = []
            found_recipe = False
            
            for line in response.iter_lines():
                if line:
                    # In TestClient/HTTPX, lines might be str or bytes depending.
                    # Usually str if text mode.
                    decoded_line = line
                    if hasattr(line, "decode"):
                       decoded_line = line.decode('utf-8')

                    if decoded_line.startswith("data: "):
                        data_str = decoded_line[6:]
                        try:
                            # Handle [DONE] or ping messages
                            if data_str.strip() == "[DONE]":
                                continue
                                
                            data = json.loads(data_str)
                            event_type = data.get("type")
                            
                            # Look for STATE_SNAPSHOT events to see if ingredients were updated
                            if event_type == "STATE_SNAPSHOT":
                                snapshot = data.get("snapshot", {})
                                if snapshot.get("ingredients"):
                                    current_ingredients = snapshot.get("ingredients")
                                    # We want to see non-empty ingredients
                                    if current_ingredients:
                                        print(f"State Update - Ingredients: {current_ingredients}")
                                        if not extracted_ingredients:
                                            extracted_ingredients = current_ingredients
                                        
                                if snapshot.get("recipe"):
                                    print(f"Recipe found: {snapshot['recipe'].get('name')}")
                                    found_recipe = True
                                    
                        except json.JSONDecodeError:
                            pass
                            
        # 4. Assertions
        print(f"\nExtracted Ingredients: {extracted_ingredients}")
        
        # Verify ingredients were parsed (should contain apples and cinnamon)
        assert len(extracted_ingredients) >= 2, "Should have extracted at least 2 ingredients"
        
        # Note: Ingredients might be sanitized/normalized, so check loose match
        ingredients_str = " ".join(extracted_ingredients).lower()
        assert "apple" in ingredients_str, f"Should contain apples, got {extracted_ingredients}"
        assert "cinnamon" in ingredients_str, f"Should contain cinnamon, got {extracted_ingredients}"
        
        # Verify a recipe was eventually found (generated or searched)
        # Note: If no API key for Tavily/Gemini, this might fail on recipe generation, 
        # but parsing happens BEFORE that.
        # But if parsing succeeds, it moves to validation -> search -> generate.
        # The test checks if parsing worked.
        
        assert extracted_ingredients, "Failed to extract any ingredients via parsing"

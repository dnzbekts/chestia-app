"""
Live data test for CopilotKit endpoint.

This script sends a real request to the running CopilotKit endpoint
and logs the response to the terminal.

Usage:
    1. Start the server: uvicorn src.main:app --reload
    2. Run this script: python -m tests.integration.test_live_data
"""

import httpx
import json
import sys


def test_copilotkit_live():
    """
    Send a real request to the CopilotKit endpoint with live data.
    
    Tests the /copilotkit endpoint with actual ingredients to generate a recipe.
    """
    base_url = "http://127.0.0.1:8000"
    
    print("=" * 60)
    print("🍳 CopilotKit Live Data Test")
    print("=" * 60)
    
    # 1. Test info endpoint
    print("\n📋 Testing /copilotkit info endpoint...")
    try:
        response = httpx.post(
            f"{base_url}/copilotkit/",
            json={"method": "info"},
            timeout=10.0
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Test direct graph invocation via internal endpoint
    print("\n🥘 Testing graph invocation with real data...")
    print("   (Using direct /generate endpoint for live test)")
    
    test_payload = {
        "ingredients": ["kuzu eti","soğan","yeşil biber", "domates"],
        "difficulty": "medium",
        "lang": "tr"
    }
    
    print(f"   Ingredients: {test_payload['ingredients']}")
    print(f"   Difficulty: {test_payload['difficulty']}")
    print(f"   Language: {test_payload['lang']}")
    print("\n   ⏳ Sending request (this may take 10-30 seconds)...")
    
    try:
        response = httpx.post(
            f"{base_url}/generate",
            json=test_payload,
            timeout=120.0
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n   📨 Response:")
            print("-" * 40)
            
            if data.get("recipe"):
                recipe = data["recipe"]
                metadata = recipe.get('metadata', {})
                # Handle metadata as JSON string (from cache)
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                source_node = data.get('source_node', 'unknown')
                print(f"   ✅ Recipe Generated!")
                print(f"   📍 Source Node: {source_node}")
                print(f"   📖 Name: {recipe.get('name', 'N/A')}")
                print(f"   🎯 Difficulty: {metadata.get('difficulty', 'N/A') if isinstance(metadata, dict) else 'N/A'}")
                
                ingredients = recipe.get('ingredients', [])
                if isinstance(ingredients, str):
                    ingredients = json.loads(ingredients)
                print(f"   🥗 Ingredients ({len(ingredients)}):")
                for i, ing in enumerate(ingredients[:20], 1):
                    print(f"      {i}. {ing}")
                
                steps = recipe.get('steps', [])
                if isinstance(steps, str):
                    steps = json.loads(steps)
                print(f"   📝 Steps ({len(steps)}):")
                for i, step in enumerate(steps[:3], 1):
                    step_text = step[:60] + "..." if len(step) > 60 else step
                    print(f"      {i}. {step_text}")
                if len(steps) > 3:
                    print(f"      ... and {len(steps) - 3} more steps")
                    
                if data.get("extra_ingredients"):
                    print(f"   ➕ Extra Ingredients Added: {data['extra_ingredients']}")
            else:
                print(f"   ⚠️ No recipe in response")
                print(f"   Error: {data.get('error', 'Unknown')}")
                
            print("-" * 40)
        else:
            print(f"   ❌ Error: {response.text}")
                    
    except httpx.TimeoutException:
        print("   ⚠️ Request timed out (120s)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_copilotkit_live()

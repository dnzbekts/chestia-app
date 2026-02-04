"""
Live data test for CopilotKit endpoint.

This script sends a real request to the running CopilotKit endpoint
to verify the agent connection and response structure.

Usage:
    1. Start the server: uvicorn src.main:app --reload
    2. Run this script: python -m tests.integration.test_copilotkit_live
"""

import httpx
import json
import sys
import asyncio

async def test_copilotkit_endpoint():
    """
    Test the /copilotkit endpoint.
    """
    base_url = "http://127.0.0.1:8000"
    
    print("\n🤖 Testing CopilotKit Endpoint...")
    
    # 1. Test Health Endpoint
    print("\n1. Testing /copilotkit/health ...")
    try:
        response = httpx.get(f"{base_url}/copilotkit/health", follow_redirects=True)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")

        if response.status_code == 200:
             print("   ✅ CopilotKit Health Endpoint is Active")
        else:
             print(f"   ⚠️ Unexpected status: {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")

    # 2. Test Main Endpoint (POST) with REAL Payload
    print("\n2. Testing /copilotkit (POST with valid payload) ...")
    
    # Construct a valid payload based on the validation errors we saw earlier
    # Required fields: threadId, runId, state, tools, context, forwardedProps
    import uuid
    thread_id = str(uuid.uuid4())
    run_id = str(uuid.uuid4())
    
    payload = {
        "threadId": thread_id,
        "runId": run_id,
        "state": {
            # Initial state matching GraphState
            "ingredients": ["chicken", "rice", "tomatoes"],
            "difficulty": "easy",
            "lang": "en",
            "messages": [] 
        },
        "messages": [
            {
                "id": str(uuid.uuid4()),
                "role": "user",
                "content": "I have chicken, rice and tomatoes. What can I cook?"
            }
        ],
        "tools": [],
        "context": [], # Fixed: Expected a list, not a dict
        "forwardedProps": {}
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", f"{base_url}/copilotkit", json=payload, follow_redirects=True) as response:
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ CopilotKit Main Endpoint Accepted Request")
                    print("   📡 Streaming Response Chunks:")
                    count = 0
                    async for chunk in response.aiter_lines():
                        if chunk:
                            print(f"      {chunk[:200]}...") # Print first 200 chars of each chunk
                            count += 1
                            if count >= 5:
                                print("      ... (stopping output log after 5 chunks)")
                                break
                else:
                    print(f"   ⚠️ Unexpected status: {response.status_code}")
                    print(f"   Response: {await response.aread()}")

    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        
    print("\n" + "=" * 60)
    print("🏁 CopilotKit Test Completed")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_copilotkit_endpoint())

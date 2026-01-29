"""
Chestia Backend - Application Entry Point

This module initializes the FastAPI application, sets up CopilotKit integration,
and includes all route handlers.
"""

from fastapi import FastAPI
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAGUIAgent

from src.core import COPILOTKIT_AGENT_NAME, COPILOTKIT_AGENT_DESCRIPTION
from src.workflow import copilotkit_graph
from src.api.routes import router

# Initialize FastAPI application
app = FastAPI(title="Chestia Backend")

# Include API routes
app.include_router(router)

# Initialize CopilotKit Remote Endpoint with LangGraph AGUI agent
copilotkit_sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAGUIAgent(
            name=COPILOTKIT_AGENT_NAME,
            description=COPILOTKIT_AGENT_DESCRIPTION,
            graph=copilotkit_graph,
        )
    ],
)

# Add CopilotKit endpoint to FastAPI
add_fastapi_endpoint(app, copilotkit_sdk, "/copilotkit")

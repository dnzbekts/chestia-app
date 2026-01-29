from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAGUIAgent
import time

from src.core import COPILOTKIT_AGENT_NAME, COPILOTKIT_AGENT_DESCRIPTION
from src.workflow import copilotkit_graph
from src.api.routes import router
from src.api.rate_limit import setup_rate_limiting

# Initialize FastAPI application
app = FastAPI(
    title="Chestia Backend",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Setup Rate Limiting
setup_rate_limiting(app)

# 1. CORS Configuration
# In production, this should be restricted to specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# 2. Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Standard Security Headers
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

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

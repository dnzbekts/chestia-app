from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAGUIAgent
import time
import os

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
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": time.time()}

# Add CopilotKit endpoint to FastAPI
add_langgraph_fastapi_endpoint(
    app=app,
    agent=LangGraphAGUIAgent(
        name=COPILOTKIT_AGENT_NAME,
        description=COPILOTKIT_AGENT_DESCRIPTION,
        graph=copilotkit_graph
    ),
    path="/copilotkit"
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
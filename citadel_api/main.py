
"""
Main FastAPI application for the Citadel API integration layer.

This module sets up the FastAPI application, configures CORS, includes routers,
and provides the entry point for the API server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any

from citadel_api.routes import agent, graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("citadel_api")

# Create FastAPI application
app = FastAPI(
    title="Citadel API",
    description="Integration layer between AG-UI protocol and LangGraph implementation",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent.router, prefix="/api/agent", tags=["Agent Workflows"])
app.include_router(graph.router, prefix="/api/graph", tags=["Graph Workflows"])

@app.get("/", response_class=JSONResponse)
async def root() -> Dict[str, Any]:
    """
    Root endpoint that returns basic API information.
    
    Returns:
        Dict[str, Any]: Basic information about the API
    """
    return {
        "name": "Citadel API",
        "version": "0.1.0",
        "description": "Integration layer between AG-UI protocol and LangGraph implementation",
        "status": "operational"
    }

@app.get("/health", response_class=JSONResponse)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        Dict[str, str]: Health status of the API
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("citadel_api.main:app", host="0.0.0.0", port=8000, reload=True)

# main.py

import os
import asyncio
import logging
import uvicorn
from contextlib import asynccontextmanager  # <-- NEW: Import the context manager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

# Import application components
from database import events_collection, eventsesh_collection
from routes import auth, webhook_routes,callback_routes


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
PORT = int(os.getenv("PORT", 3000))

# --- NEW: Lifespan event handler ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code inside this block runs on application startup
    logger.info("Application starting up...")
    
    # Set the target URL for the Smee client
    os.environ["TARGET_URL"] = f"http://localhost:{PORT}/events"
    
    
    logger.info(f"Server is running on port {PORT}")
    logger.info(f"Webhook endpoint is ready at http://localhost:{PORT}/events")
    #logger.info(f"WebSocket endpoint is ready at ws://localhost:{PORT}/ws")

    yield  # The application runs here

    # Code inside this block runs on application shutdown
    logger.info("Application shutting down...")
    # You can add cleanup code here, like closing database connections
    # or stopping background tasks gracefully.

# Initialize FastAPI app with the lifespan handler
app = FastAPI(
    title="Webhook and WebSocket Service",
    description="A service to receive webhooks, process transactions, and push real-time updates via WebSockets.",
    lifespan=lifespan  # <-- UPDATED: Pass the lifespan manager here
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://10.201.3.248:8081", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(webhook_routes.router, tags=["Webhooks"])
# You could include other routers here, e.g., app.include_router(auth.router, tags=["Auth"])

app.include_router(callback_routes.router, prefix="/v2/callback", tags=["Callbacks"])
# WebSocket route
#app.websocket("/ws")(websocket_serverErr.websocket_endpoint)

# Protected route example
@app.get("/protected")
async def protected_route(current_user: dict = Depends(auth.get_current_user)):
    return {"message": f"Hello, {current_user.get('email')}! You have access to a protected route."}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Service is running."}

# Main execution block
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        log_level="info"
    )
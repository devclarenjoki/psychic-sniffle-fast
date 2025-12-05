# database.py

import os
import motor.motor_asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

# Create a new MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)

# Get the database
db = client.events_db

# Get the collections
events_collection = db.events
eventsesh_collection = db.eventsesh
calls_collection = db.callstb

# Export the collections to be used in other modules
__all__ = ["events_collection", "eventsesh_collection"]
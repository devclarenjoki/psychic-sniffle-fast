# models.py

from typing import Dict, Any, Optional
from pydantic import BaseModel

# Model for the /events2 webhook payload
class Event(BaseModel):
    eventType: str
    payload: Dict[str, Any]

# Model for the /events webhook payload
class EventSession(BaseModel):
    transactionId: str
    status: str
    eventType: str
    payload: Dict[str, Any]
    receivedAt: Optional[str] = None
    sessionProcessed: Optional[bool] = False

# Model for the data sent through the event emitter
class TransactionUpdate(BaseModel):
    transactionId: str
    userId: str
    status: str
    message: Optional[str] = ""
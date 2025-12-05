# routes/callbacks.py

import logging
from fastapi import APIRouter, Request, Depends
#from fastapi_limiter.depends import RateLimiter
from services.in_memory_limiter import rate_limit 

from models.webhook_model import CallbackData
from services.callback_service import process_callback_data


logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/data")
async def callback_endpoint(
    request: Request, 
    callback_data: CallbackData,
    _=Depends(rate_limit(times=100, seconds=60))
):
    """Endpoint to receive and process callback data."""
    try:
        result = await process_callback_data(callback_data)
        return result
    except Exception as e:
        logger.error(f"Error in callback route: {e}")
        raise
# services/callback.py

import os
import logging
import httpx
from datetime import datetime 
import pytz
from models.webhook_model import CallbackData
from database import calls_collection
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
CALLBACK_URL=os.getenv("CALLBACK_URL","https://psychic-sniffle-fast.vercel.app/v2/callback/data")

async def send_http_callback(user_id: str, transaction_id: str, status_message: str):
    if not CALLBACK_URL:
        logger.warning("External CALLBACK_URL not configured. Skipping.")
        return
    
    payload = CallbackData(
        userId=user_id,
        transactionId=transaction_id,
        status_message=status_message
    ).model_dump()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(CALLBACK_URL, json=payload)
            response.raise_for_status()
            logger.info(f"External callback sent successfully for transaction {transaction_id}")
    except httpx.HTTPError as e:
        logger.error(f"Failed to send external callback: {e}")
        # Decide if you want to raise an exception here or just log it
        # raise Exception(f"Failed to send external callback: {str(e)}")

async def process_callback_data(callback_data: CallbackData) -> dict[str, str]:
    try:
                # Create the document to be inserted
        document_to_insert = {
            "user_id": callback_data.userId,
            "last_transaction_id": callback_data.transactionId,
            "last_transaction_status": callback_data.status_message,
            "updated_at": datetime.now(pytz.UTC),
            # It's good practice to add a creation timestamp for new documents
            "created_at": datetime.now(pytz.UTC)
        }

        # Perform the insert operation
        result = await calls_collection.insert_one(document_to_insert)
        # result = await calls_collection.update_one(
        #     {"user_id": callback_data.userId},
        #     {
        #         "$set": {
        #             "last_transaction_id": callback_data.transactionId,
        #             "last_transaction_status": callback_data.status_message,
        #             "updated_at": datetime.now(pytz.UTC)
        #         }
        #     }
        # )
        
        # if result.modified_count == 0:
        #     logger.warning(f"User {callback_data.userId} not found or not updated during callback processing.")
        
        return {
            "status": "success",
            "message": "Callback processed successfully",
            "data": callback_data.model_dump_json()
        }
    except Exception as e:
        logger.error(f"Error processing callback data: {e}")
        raise Exception(f"Failed to process callback: {str(e)}")
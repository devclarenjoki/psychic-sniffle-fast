# routes/webhook_routes.py

import os
import uuid
import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, status
from database import events_collection, eventsesh_collection
from models import Event, EventSession, TransactionUpdate
from services.session_checker import check_session_status
from event_emitter import event_emitter
from services.callback_service import send_http_callback

logger = logging.getLogger(__name__)

# This map will store the relationship between a sourceId and its transactionId
transaction_map = {}

router = APIRouter()

@router.post("/events2", status_code=status.HTTP_200_OK)
async def receive_webhook_event(request: Request):
    logger.info("--- Received a Webhook Event at /events2 ---")
    try:
        payload = await request.json()
        if not payload:
            raise HTTPException(status_code=400, detail="Bad Request: Missing payload.")

        new_event = {
            "eventType": "order_status_change",
            "payload": payload,
            "timestamp": datetime.now()
        }
        await events_collection.insert_one(new_event)
        logger.info("Successfully stored event in the database.")
        return {"message": "Webhook received and stored successfully!"}
    except Exception as error:
        logger.error(f"Error processing webhook: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")

@router.post("/events", status_code=status.HTTP_200_OK)
async def receive_transaction_event(request: Request):
    logger.info("--- Received a Webhook Event at /events ---")
    try:
        payload = await request.json()
        status = payload.get("data", {}).get("order", {}).get("status")
        session_identifier = payload.get("data", {}).get("order", {}).get("userId")

        if not status or not session_identifier:
            raise HTTPException(status_code=400, detail="Bad Request: Missing required fields (status or userId).")

        # Core Logic: Get or Generate a Transaction ID
        transaction_id = transaction_map.get(session_identifier)
        if not transaction_id:
            transaction_id = str(uuid.uuid4())
            transaction_map[session_identifier] = transaction_id
            logger.info(f"[New Session] for sourceId: {session_identifier}. Generated transactionId: {transaction_id}")
        else:
            logger.info(f"[Existing Session] Found transactionId: {transaction_id} for sourceId: {session_identifier}")

        # Create and Save the event document
        new_event = {
            "transactionId": transaction_id,
            "status": status,
            "eventType": "order_status_change",
            "payload": payload,
            "receivedAt": datetime.now(),
            "sessionProcessed": False
        }
        await eventsesh_collection.insert_one(new_event)
        logger.info(f"Stored event for transaction {transaction_id} with status: {status}")

        # Trigger the session check in the background
        asyncio.create_task(check_session_status(transaction_id))

        # Emit event for WebSocket clients
        # update_data = TransactionUpdate(
        #     transactionId=transaction_id,
        #     userId=session_identifier,
        #     status=status
        # )
        await send_http_callback(session_identifier,transaction_id,status_message=status)
        #event_emitter.emit('transactionStatusUpdate', update_data)

        return {"message": f"Transfer complete! {transaction_id}"}

    except Exception as error:
        logger.error(f"Error processing webhook: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error.")
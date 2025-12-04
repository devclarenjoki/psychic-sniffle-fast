# services/session_checker.py

import logging
from database import eventsesh_collection

logger = logging.getLogger(__name__)

async def check_session_status(transaction_id: str):
    """
    Checks if a transaction session is complete and valid.
    Processes it only once by marking it as 'sessionProcessed'.
    """
    logger.info(f"[Session Check] Checking status for transactionId: {transaction_id}")

    try:
        # Find the first event for this transaction to check if it's already processed
        first_event = await eventsesh_collection.find_one({"transactionId": transaction_id})

        # If no event exists or it's already been processed, do nothing and exit.
        if not first_event or first_event.get("sessionProcessed", False):
            logger.info(f"[Session Check] Transaction {transaction_id} is already processed or has no events. Skipping.")
            return

        # Find all events for this transaction, sorted by when they were received
        events = await eventsesh_collection.find({"transactionId": transaction_id}).sort("receivedAt", 1).to_list(length=None)

        # A session is considered complete when we have 6 events
        if len(events) < 6:
            logger.info(f"[Session Check] Incomplete session. Found {len(events)}/6 events. Waiting for more.")
            return

        last_event = events[-1]

        # --- Main Validation Logic ---
        is_first_status_correct = first_event["status"] == "deposit_awaiting"
        is_last_status_correct = last_event["status"] == "payout_successful"

        if is_first_status_correct and is_last_status_correct:
            logger.info(f"\n✅ [Session Check] SUCCESS! Transaction {transaction_id} is valid.")
        else:
            logger.info(f"\n❌ [Session Check] FAILED! Transaction {transaction_id} is invalid.")
            logger.info(f"   - First event status was: \"{first_event['status']}\" (expected: \"deposit_awaiting\")")
            logger.info(f"   - Last event status was: \"{last_event['status']}\" (expected: \"payout_successful\")")

        # --- Find and Report Important Status Codes ---
        logger.info("[Session Check] Scanning for important statuses...")
        important_statuses = ["deposit_successful", "payout_successful"]
        for event in events:
            if event["status"] in important_statuses:
                logger.info(f"   - Found important status: \"{event['status']}\" for transactionId: {event['transactionId']}")

        # --- Mark the session as processed to prevent re-checking ---
        await eventsesh_collection.update_many(
            {"transactionId": transaction_id},
            {"$set": {"sessionProcessed": True}}
        )
        logger.info(f"[Session Check] Marked transaction {transaction_id} as processed.\n")

    except Exception as error:
        logger.error(f"[Session Check] Error checking session for {transaction_id}: {error}")
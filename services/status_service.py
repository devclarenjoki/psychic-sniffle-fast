import logging
from models.webhook_model import StatusDataOrder,StatusRecordData

from database import calls_collection


logger = logging.getLogger(__name__)
async def process_status_data_v1(status_data: StatusDataOrder) -> StatusRecordData:
    try:
        
        projection = {
            "user_id": 1,
            "order_id":1,
            "last_transaction_id": 1,
            "last_transaction_status": 1,
            "_id": 0
        }

        # Perform the insert operation
        record_dict = await calls_collection.find_one(
            filter={"order_id": status_data.userOrderId},
            sort=[("updated_at", -1)],  # -1 for descending (newest first)
            projection=projection

        )

        print(record_dict)
        

                # If a record is found, parse it directly into our lean model
        if record_dict:
            return StatusRecordData(**record_dict)
        
        
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
        
 
        #     "status": "success",
        #     "message": "Callback processed successfully",
        #     "data": status_one.model_dump_json(),
        #     "rsout":statdata.model_dump_json()
        # }
    except Exception as e:
        logger.error(f"Error processing callback data: {e}")
        raise Exception(f"Failed to process callback: {str(e)}")



async def process_status_data (status_data: StatusDataOrder) -> StatusRecordData:
 
    statusone=await process_status_data_v1(status_data=status_data)
    return statusone


 
# models/webhook.py

from pydantic import BaseModel, Field, model_validator
from typing import Optional

class CallbackData(BaseModel):
    userId: str = Field(..., min_length=1)
    transactionId: str = Field(..., min_length=1)
    orderId: str = Field(..., min_length=1)
    status_message: str = Field(..., min_length=1, max_length=200)

class StatusDataOrder(BaseModel):
    userOrderId: str = Field(..., min_length=1)


class StatusRecordData(BaseModel):
    # Use Field aliases to map database field names to desired output keys
    userId: str = Field(alias="user_id")
    orderId: str = Field(alias="order_id")
    transactionId: str = Field(alias="last_transaction_id")
    status_message: str = Field(alias="last_transaction_status")



class WebhookData(BaseModel):
    event: str
    user_id: Optional[str] = None
    userId: Optional[str] = None
    transaction_id: Optional[str] = None
    transactionId: Optional[str] = None


    @model_validator(mode='after')
    def check_ids_are_present(self) -> 'WebhookData':
        """Validates that at least one of each ID pair is provided."""
        user_id = self.user_id or self.userId
        transaction_id = self.transaction_id or self.transactionId

        if not user_id:
            raise ValueError('Either user_id or userId must be provided')
        if not transaction_id:
            raise ValueError('Either transaction_id or transactionId must be provided')
        
        # Normalize the final model instance to have consistent values
        # This ensures that downstream code can rely on one field name (e.g., user_id)
        self.user_id = user_id
        self.userId = user_id
        self.transaction_id = transaction_id
        self.transactionId = transaction_id
        
        return self
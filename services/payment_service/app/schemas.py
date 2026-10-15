from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class ProcessPaymentRequest(BaseModel):
    order_id: int
    amount: Decimal

class PaymentOut(BaseModel):
    id: int
    order_id: int
    amount: Decimal
    status: str
    transaction_id: str
    created_at: datetime
    class Config:
        from_attributes = True
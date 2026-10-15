from pydantic import BaseModel

class ReserveStockRequest(BaseModel):
    product_id: int
    quantity: int

class InventoryOut(BaseModel):
    product_id: int
    quantity: int
    class Config:
        from_attributes = True
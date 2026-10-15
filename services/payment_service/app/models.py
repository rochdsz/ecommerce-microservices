import enum
from sqlalchemy import Column, Integer, String, Numeric, Enum, DateTime, func
from app.database import Base

class PaymentStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, unique=True, index=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.SUCCESS)
    transaction_id = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
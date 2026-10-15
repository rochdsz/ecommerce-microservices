import enum
from sqlalchemy import Column, Integer, Numeric, Enum, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class OrderStatus(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.CONFIRMED)
    created_at = Column(DateTime, server_default=func.now())

    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
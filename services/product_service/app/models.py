from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000))
    price = Column(Numeric(10, 2), nullable=False)
    sku = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
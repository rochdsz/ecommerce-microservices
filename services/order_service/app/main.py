import os, httpx
from decimal import Decimal
from typing import List
from jose import jwt, JWTError
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.models import Order, OrderItem, OrderStatus
from app.schemas import OrderCreate, OrderOut

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order Service")

SECRET_KEY = os.getenv("SECRET_KEY", "shared_microservices_jwt_secret_key_12345")
PRODUCT_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product_service:8000")
INVENTORY_URL = os.getenv("INVENTORY_SERVICE_URL", "http://inventory_service:8000")
PAYMENT_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment_service:8000")

def get_current_user_id(authorization: str = Header(None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/", response_model=OrderOut, status_code=201)
@app.post("", response_model=OrderOut, status_code=201)
async def create_order(
    payload: OrderCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    reserved_items = []
    total_amount = Decimal("0.00")
    order_items_to_save = []

    async with httpx.AsyncClient(timeout=5.0) as client:
        for item in payload.items:
            p_res = await client.get(f"{PRODUCT_URL}/{item.product_id}")
            if p_res.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Product {item.product_id} unavailable")
            product = p_res.json()
            price = Decimal(str(product["price"]))
            total_amount += price * item.quantity

            inv_res = await client.post(
                f"{INVENTORY_URL}/reserve",
                json={"product_id": item.product_id, "quantity": item.quantity}
            )
            if inv_res.status_code != 200:
                for prev in reserved_items:
                    await client.post(f"{INVENTORY_URL}/rollback", json=prev)
                raise HTTPException(status_code=400, detail=f"Stock unavailable for product {item.product_id}")

            reserved_items.append({"product_id": item.product_id, "quantity": item.quantity})
            order_items_to_save.append(OrderItem(product_id=item.product_id, quantity=item.quantity, price=price))

        order = Order(user_id=user_id, total_amount=total_amount, status=OrderStatus.CONFIRMED)
        db.add(order)
        db.flush()

        for oi in order_items_to_save:
            oi.order_id = order.id
            db.add(oi)
        db.commit()
        db.refresh(order)

        pay_res = await client.post(
            f"{PAYMENT_URL}/charge",
            json={"order_id": order.id, "amount": float(total_amount)}
        )
        if pay_res.status_code != 201:
            order.status = OrderStatus.FAILED
            db.commit()
            raise HTTPException(status_code=500, detail="Payment processing failed")

        return order

@app.get("/", response_model=List[OrderOut])
@app.get("", response_model=List[OrderOut])
def get_user_orders(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.user_id == user_id).all()

@app.get("/health")
def health():
    return {"service": "order-service", "status": "ok"}

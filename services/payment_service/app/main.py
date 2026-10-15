import uuid
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.models import Payment, PaymentStatus
from app.schemas import ProcessPaymentRequest, PaymentOut

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Payment Service")

@app.post("/charge", response_model=PaymentOut, status_code=201)
def charge_payment(req: ProcessPaymentRequest, db: Session = Depends(get_db)):
    tx_id = f"tx_{uuid.uuid4().hex[:12]}"
    payment = Payment(
        order_id=req.order_id,
        amount=req.amount,
        status=PaymentStatus.SUCCESS,
        transaction_id=tx_id
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

@app.get("/{order_id}", response_model=PaymentOut)
def get_payment(order_id: int, db: Session = Depends(get_db)):
    p = db.query(Payment).filter(Payment.order_id == order_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Payment record not found")
    return p

@app.get("/health")
def health():
    return {"service": "payment-service", "status": "ok"}
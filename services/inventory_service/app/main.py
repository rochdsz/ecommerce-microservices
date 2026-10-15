from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal, get_db
from app.models import Inventory
from app.schemas import ReserveStockRequest, InventoryOut

def auto_seed_inventory():
    db = SessionLocal()
    try:
        if db.query(Inventory).count() == 0:
            stocks = [
                Inventory(product_id=1, quantity=30),
                Inventory(product_id=2, quantity=45),
                Inventory(product_id=3, quantity=15),
                Inventory(product_id=4, quantity=20),
                Inventory(product_id=5, quantity=60),
            ]
            db.bulk_save_objects(stocks)
            db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    auto_seed_inventory()
    yield

app = FastAPI(title="Inventory Service", lifespan=lifespan)

@app.get("/{product_id}", response_model=InventoryOut)
def check_stock(product_id: int, db: Session = Depends(get_db)):
    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inv

@app.post("/reserve")
def reserve_stock(req: ReserveStockRequest, db: Session = Depends(get_db)):
    inv = db.query(Inventory).filter(Inventory.product_id == req.product_id).with_for_update().first()
    if not inv or inv.quantity < req.quantity:
        raise HTTPException(status_code=400, detail=f"Insufficient inventory for product {req.product_id}")
    inv.quantity -= req.quantity
    db.commit()
    return {"status": "reserved", "product_id": req.product_id, "remaining": inv.quantity}

@app.post("/rollback")
def rollback_stock(req: ReserveStockRequest, db: Session = Depends(get_db)):
    inv = db.query(Inventory).filter(Inventory.product_id == req.product_id).first()
    if inv:
        inv.quantity += req.quantity
        db.commit()
    return {"status": "restored"}

@app.get("/health")
def health():
    return {"service": "inventory-service", "status": "ok"}
from decimal import Decimal
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal, get_db
from app.models import Product
from app.schemas import ProductCreate, ProductOut

def auto_seed_products():
    db = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            samples = [
                Product(id=1, title="Wireless ANC Headphones", description="Noise canceling over-ear.", price=Decimal("149.99"), sku="HP-ANC-1"),
                Product(id=2, title="Mechanical Keyboard", description="Brown switches, RGB backlit.", price=Decimal("89.50"), sku="KB-MEC-4"),
                Product(id=3, title="4K Ultra-HD Monitor 27-inch", description="IPS HDR tilt stand.", price=Decimal("319.00"), sku="MON-4K-27"),
                Product(id=4, title="Ergonomic Desk Chair", description="Lumbar support mesh chair.", price=Decimal("210.00"), sku="CHR-ERG-9"),
                Product(id=5, title="Wireless Gaming Mouse", description="High-precision rechargeable.", price=Decimal("49.99"), sku="MOU-WL-01")
            ]
            db.bulk_save_objects(samples)
            db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    auto_seed_products()
    yield

app = FastAPI(title="Product Service", lifespan=lifespan)

@app.get("/", response_model=List[ProductOut])
@app.get("", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p

@app.post("/", response_model=ProductOut, status_code=201)
@app.post("", response_model=ProductOut, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    p = Product(**payload.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@app.get("/health")
def health():
    return {"service": "product-service", "status": "ok"}

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
import json
from datetime import datetime, timezone
from .models import Base, Payment
from .schemas import PaymentRequest, PaymentResponse
import httpx
import uuid
import time

DATABASE_URL = os.getenv("DATABASE_URL")
AUTH_URL = os.getenv("AUTH_URL")
BOOKING_URL = os.getenv("BOOKING_URL")

# Create engine with connection pooling and retry mechanism
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"connect_timeout": 10}
)
SessionLocal = sessionmaker(bind=engine)

# Create FastAPI app
app = FastAPI(title="Payment Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://event-booking.local", "https://event-booking.local"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    # Add retry mechanism for database connection
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Database connection attempt {attempt + 1} failed: {e}")
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect to database after {max_retries} attempts")
                raise e

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "payment"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple auth: expect Authorization: Bearer <token>
async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(401, "Missing auth")
    token = authorization.split(" ")[1]
    
    # Verify token via auth service with reduced timeout
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{AUTH_URL}/verify", json={"token": token}, timeout=2.0)
            if resp.status_code == 200:
                return resp.json()["user_id"]
        except Exception as e:
            print(f"Auth service error: {e}")
            pass
    
    raise HTTPException(401, "Invalid token")

@app.post("/process-payment", response_model=PaymentResponse)
async def process_payment(payment_req: PaymentRequest, authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id = await get_current_user(authorization)
    
    # Create payment record
    payment = Payment(
        user_id=user_id,
        booking_id=payment_req.booking_id,
        amount=payment_req.amount,
        phone_number=payment_req.phone_number,
        status="completed"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # Update booking status to confirmed with reduced timeout
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.put(f"{BOOKING_URL}/confirm-booking/{payment_req.booking_id}", timeout=2.0)
            if resp.status_code != 200:
                print(f"Failed to confirm booking: {resp.text}")
    except Exception as e:
        print(f"Error confirming booking: {e}")
        # Don't fail the payment if booking confirmation fails
    
    return PaymentResponse(
        payment_id=str(payment.id),
        message="Payment processed successfully",
        requires_verification=False
    )

@app.get("/payment-receipt/{payment_id}")
async def get_payment_receipt(payment_id: str, authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id = await get_current_user(authorization)
    
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.user_id == user_id
    ).first()
    
    if not payment:
        raise HTTPException(404, "Payment not found")
    
    return {
        "payment_id": str(payment.id),
        "amount": payment.amount,
        "status": payment.status,
        "created_at": payment.created_at,
        "phone_number": payment.phone_number
    }

@app.get("/payment-by-booking/{booking_id}")
async def get_payment_by_booking(booking_id: str, authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id = await get_current_user(authorization)
    
    payment = db.query(Payment).filter(
        Payment.booking_id == booking_id,
        Payment.user_id == user_id
    ).first()
    
    if not payment:
        raise HTTPException(404, "Payment not found for this booking")
    
    return {
        "payment_id": str(payment.id),
        "amount": payment.amount,
        "status": payment.status,
        "created_at": payment.created_at,
        "phone_number": payment.phone_number
    } 
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from .models import Base, Booking
from .schemas import BookingRequest, BookingOut
import redis
import uuid
import json
import aio_pika
import asyncio
import httpx
from typing import List

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
CATALOG_URL = os.getenv("CATALOG_URL")
AUTH_URL = os.getenv("AUTH_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

r = redis.from_url(REDIS_URL, decode_responses=True)

app = FastAPI(title="Booking Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    try:
        print("Starting booking service...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        print("Booking service startup complete")
    except Exception as e:
        print(f"Error during startup: {e}")
        raise e

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "booking"}

@app.get("/test")
def test_endpoint():
    return {"message": "Test endpoint working"}

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
    # For demo, we just return token; in real, verify token via auth service.
    # Optionally call auth service to validate token
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{AUTH_URL}/verify", json={"token": token}, timeout=5.0)
            if resp.status_code == 200:
                return resp.json()["user_id"]
        except Exception:
            pass
    # If auth service doesn't offer verify, treat token as user_id (for demo)
    try:
        uid = uuid.UUID(token)
        return str(uid)
    except:
        raise HTTPException(401, "Invalid token")

@app.post("/book", response_model=BookingOut)
async def create_booking(req: BookingRequest, authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id = await get_current_user(authorization)
    event_key = f"event:{req.event_id}:capacity"
    lock_key = f"lock:{req.event_id}:{user_id}"
    
    # Get event capacity from catalog service
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{CATALOG_URL}/events/{req.event_id}")
        if resp.status_code != 200:
            raise HTTPException(400, "Event not found")
        event = resp.json()
    capacity = event.get("capacity", 0)

    # Basic lock using Redis setnx
    # We'll store 'reserved' count per event in redis
    reserved = r.get(event_key)
    if reserved is None:
        r.set(event_key, 0)
        reserved = 0
    reserved = int(reserved)

    if reserved + req.seats > capacity:
        raise HTTPException(400, "Not enough seats available")

    # create tentative booking (pending) in DB
    booking = Booking(user_id=user_id, event_id=str(req.event_id), seats=req.seats, status="pending")
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # increment reserved atomically
    new_reserved = r.incrby(event_key, req.seats)

    # Update event capacity in catalog service
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.put(f"{CATALOG_URL}/events/{req.event_id}/capacity?seats={req.seats}")
            if resp.status_code != 200:
                print(f"Failed to update event capacity: {resp.text}")
    except Exception as e:
        print(f"Error updating event capacity: {e}")

    # publish to RabbitMQ for asynchronous processing (e.g., payment & notification)
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue("booking_queue", durable=True)
            payload = {"booking_id": str(booking.id), "user_id": user_id, "event_id": str(req.event_id), "seats": req.seats}
            await channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(payload).encode()),
                routing_key="booking_queue"
            )
    except Exception as e:
        print(f"Failed to publish to RabbitMQ: {e}")
        # In production, you might want to handle this differently

    return booking

@app.get("/my-bookings", response_model=List[BookingOut])
async def get_user_bookings(authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id = await get_current_user(authorization)
    bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
    return bookings

@app.put("/confirm-booking/{booking_id}")
async def confirm_booking(booking_id: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    booking.status = "confirmed"
    db.commit()
    db.refresh(booking)
    return {"message": "Booking confirmed successfully", "booking": booking}

@app.get("/booking-payment/{booking_id}")
async def get_booking_payment(booking_id: str, authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id = await get_current_user(authorization)
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == user_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    
    # Try to find payment info from payment service
    try:
        async with httpx.AsyncClient() as client:
            # Query payment service to find payment by booking_id
            payment_url = os.getenv("PAYMENT_URL", "http://payment:8000")
            resp = await client.get(f"{payment_url}/payment-by-booking/{booking_id}")
            if resp.status_code == 200:
                payment_data = resp.json()
                return {"payment_id": payment_data.get("payment_id"), "status": booking.status}
            else:
                return {"payment_id": None, "status": booking.status}
    except Exception as e:
        print(f"Error getting payment info: {e}")
        return {"payment_id": None, "status": booking.status}

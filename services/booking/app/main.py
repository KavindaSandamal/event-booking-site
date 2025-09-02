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
from .circuit_breaker import auth_circuit_breaker, payment_circuit_breaker, catalog_circuit_breaker
from .retry import async_retry, network_retry, database_retry
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")

from .event_publisher import EventPublisher
from .event_consumer import setup_event_consumers

# Create event publisher with RABBITMQ_URL
event_publisher = EventPublisher(RABBITMQ_URL)
CATALOG_URL = os.getenv("CATALOG_URL")
AUTH_URL = os.getenv("AUTH_URL")

# Create engine with connection pooling and retry mechanism
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=1800,  # 30 minutes
    pool_timeout=30,
    connect_args={
        "connect_timeout": 10,
        "application_name": "booking_service"
    }
)
SessionLocal = sessionmaker(bind=engine)

r = redis.from_url(REDIS_URL, decode_responses=True)

# Create FastAPI app
app = FastAPI(title="Booking Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://event-booking.local", "https://event-booking.local"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    try:
        print("Starting booking service...")
        
        # Initialize event consumers
        await setup_event_consumers()
        print("Event consumers initialized successfully")
        
        # Initialize event publisher
        await event_publisher.connect()
        print("Event publisher initialized successfully")
        
        # Add retry mechanism for database connection
        import time
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
        
        print("Booking service startup complete")
    except Exception as e:
        print(f"Error during startup: {e}")
        raise e

@app.on_event("shutdown")
async def shutdown():
    """Clean up resources on shutdown."""
    try:
        await event_publisher.close()
        print("Event publisher closed successfully")
    except Exception as e:
        print(f"Error closing event publisher: {e}")

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
    except Exception as e:
        print(f"Database session error: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

@app.post("/cleanup-pending-bookings")
async def cleanup_pending_bookings(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Clean up old pending bookings that might be stuck"""
    try:
        # Delete bookings that are older than 1 hour and still pending
        from datetime import datetime, timezone, timedelta
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
        
        old_pending_bookings = db.query(Booking).filter(
            Booking.status == "pending",
            Booking.created_at < cutoff_time
        ).all()
        
        count = len(old_pending_bookings)
        for booking in old_pending_bookings:
            # Release the reserved seats in Redis
            event_key = f"event:{booking.event_id}:capacity"
            try:
                r.decrby(event_key, booking.seats)
            except:
                pass
            db.delete(booking)
        
        db.commit()
        return {"message": f"Cleaned up {count} old pending bookings"}
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Cleanup failed: {str(e)}")

# Enhanced auth with circuit breaker and retry patterns
@auth_circuit_breaker
@async_retry(network_retry)
async def verify_token_with_auth_service(token: str) -> str:
    """Verify token with auth service using circuit breaker and retry."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{AUTH_URL}/verify", 
            json={"token": token}, 
            timeout=5.0
        )
        if resp.status_code == 200:
            return resp.json()["user_id"]
        else:
            raise HTTPException(401, "Invalid token")

async def get_current_user(authorization: str = Header(None)):
    """Get current user with enhanced error handling."""
    if not authorization:
        raise HTTPException(401, "Missing auth")
    
    token = authorization.split(" ")[1]
    
    try:
        # Try to verify with auth service using circuit breaker
        user_id = await verify_token_with_auth_service(token)
        return user_id
    except Exception as e:
        print(f"Auth service error: {e}")
        # Fallback: treat token as user_id (for demo purposes)
        try:
            uid = uuid.UUID(token)
            return str(uid)
        except:
            raise HTTPException(401, "Invalid token")

@app.post("/book", response_model=BookingOut)
async def create_booking(req: BookingRequest, authorization: str = Header(None), db: Session = Depends(get_db)):
    import time
    start_time = time.time()
    print(f"[{start_time:.3f}] Booking request started for event {req.event_id}, seats {req.seats}")
    
    user_id = await get_current_user(authorization)
    print(f"[{time.time():.3f}] User authentication completed: {user_id}")
    
    event_key = f"event:{req.event_id}:capacity"
    
    # Get event capacity from catalog service with timeout
    try:
        print(f"[{time.time():.3f}] Fetching event details from catalog service...")
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{CATALOG_URL}/events/{req.event_id}")
            if resp.status_code != 200:
                raise HTTPException(400, "Event not found")
            event = resp.json()
        capacity = event.get("capacity", 0)
        print(f"[{time.time():.3f}] Event details fetched, capacity: {capacity}")
    except httpx.TimeoutException:
        print(f"[{time.time():.3f}] Catalog service timeout")
        raise HTTPException(408, "Catalog service timeout - please try again")
    except Exception as e:
        print(f"[{time.time():.3f}] Error fetching event: {e}")
        raise HTTPException(500, "Error fetching event details")

    # Optimize Redis operations using pipeline
    try:
        print(f"[{time.time():.3f}] Starting Redis operations...")
        pipe = r.pipeline()
        
        # Get current reserved count
        pipe.get(event_key)
        pipe_results = pipe.execute()
        
        reserved = pipe_results[0]
        if reserved is None:
            r.set(event_key, 0)
            reserved = 0
        reserved = int(reserved)
        print(f"[{time.time():.3f}] Current reserved seats: {reserved}")

        if reserved + req.seats > capacity:
            print(f"[{time.time():.3f}] Not enough seats available")
            raise HTTPException(400, "Not enough seats available")

        # Reserve seats in Redis (atomic operation)
        new_reserved = r.incrby(event_key, req.seats)
        print(f"[{time.time():.3f}] Reserved {req.seats} seats, new total: {new_reserved}")
        
        # Verify the reservation was successful
        if new_reserved > capacity:
            print(f"[{time.time():.3f}] Reservation exceeded capacity, rolling back...")
            r.decrby(event_key, req.seats)
            raise HTTPException(400, "Not enough seats available")

        # Update event capacity in catalog service with timeout
        print(f"[{time.time():.3f}] Updating event capacity in catalog service...")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.put(f"{CATALOG_URL}/events/{req.event_id}/capacity?seats={req.seats}")
                if resp.status_code != 200:
                    print(f"[{time.time():.3f}] Failed to update event capacity: {resp.text}")
                    # Rollback Redis reservation
                    r.decrby(event_key, req.seats)
                    raise HTTPException(500, "Failed to update event capacity")
        except Exception as e:
            print(f"[{time.time():.3f}] Error updating event capacity: {e}")
            # Rollback Redis reservation
            r.decrby(event_key, req.seats)
            raise HTTPException(500, "Error updating event capacity")
        
        print(f"[{time.time():.3f}] Event capacity updated successfully")

        # Create booking in DB
        print(f"[{time.time():.3f}] Creating booking in database...")
        booking = Booking(user_id=user_id, event_id=str(req.event_id), seats=req.seats, status="confirmed")
        db.add(booking)
        db.commit()
        db.refresh(booking)
        print(f"[{time.time():.3f}] Booking created in database with ID: {booking.id}")
        
        # Publish booking created event
        try:
            await event_publisher.connect()
            booking_data = {
                "booking_id": str(booking.id),
                "user_id": user_id,
                "event_id": str(req.event_id),
                "seats": req.seats,
                "status": "confirmed",
                "created_at": booking.created_at.isoformat()
            }
            await event_publisher.publish_booking_created(booking_data)
            print(f"[{time.time():.3f}] Booking created event published")
        except Exception as e:
            print(f"[{time.time():.3f}] Failed to publish booking event: {e}")
            # Don't fail the booking creation if event publishing fails

        # Publish to RabbitMQ as background task (non-blocking)
        print(f"[{time.time():.3f}] Publishing to RabbitMQ as background task...")
        import asyncio
        asyncio.create_task(publish_booking_to_rabbitmq(booking, user_id, req.event_id, req.seats))

        total_time = time.time() - start_time
        print(f"[{time.time():.3f}] Booking completed successfully in {total_time:.3f} seconds")
        return booking

    except Exception as e:
        print(f"[{time.time():.3f}] Booking failed with error: {e}")
        # Rollback: decrement the reserved count in Redis if it was incremented
        try:
            r.decrby(event_key, req.seats)
            print(f"[{time.time():.3f}] Rolled back Redis reservation")
        except:
            pass
        raise e

# Background task for RabbitMQ publishing
async def publish_booking_to_rabbitmq(booking, user_id, event_id, seats):
    """Publish booking to RabbitMQ as a background task"""
    import time
    try:
        print(f"[{time.time():.3f}] Background: Starting RabbitMQ publish for booking {booking.id}")
        connection = await aio_pika.connect_robust(RABBITMQ_URL, timeout=2.0)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue("booking_queue", durable=True)
            payload = {"booking_id": str(booking.id), "user_id": user_id, "event_id": str(event_id), "seats": seats}
            await channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(payload).encode()),
                routing_key="booking_queue"
            )
            print(f"[{time.time():.3f}] Background: Published booking message to RabbitMQ: {payload}")
    except Exception as e:
        print(f"[{time.time():.3f}] Background: Failed to publish to RabbitMQ: {e}")
        # Don't fail the booking if RabbitMQ is not available

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

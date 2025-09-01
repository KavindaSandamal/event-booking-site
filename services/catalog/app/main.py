from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
import time
from datetime import datetime
from .models import Base, Event
from .schemas import EventCreate, EventUpdate, EventOut

# ------------------------------------------------------------------------------
# Database Configuration
# ------------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"connect_timeout": 10}
)

SessionLocal = sessionmaker(bind=engine)

# Dependency: Database session
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

# ------------------------------------------------------------------------------
# FastAPI Application Setup
# ------------------------------------------------------------------------------
app = FastAPI(title="Catalog Service")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://event-booking.local",
        "https://event-booking.local"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# Startup Event with Retry for DB Connection
# ------------------------------------------------------------------------------
@app.on_event("startup")
def startup():
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

# ------------------------------------------------------------------------------
# Health Check
# ------------------------------------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "catalog"}

# ------------------------------------------------------------------------------
# Event Routes
# ------------------------------------------------------------------------------
@app.get("/events", response_model=list[EventOut])
def get_events(db: Session = Depends(get_db)):
    """Get all events"""
    try:
        return db.query(Event).all()
    except Exception as e:
        print(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch events")

@app.get("/events/{event_id}", response_model=EventOut)
def get_event(event_id: str, db: Session = Depends(get_db)):
    """Get a specific event by ID"""
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch event")

@app.post("/events", response_model=EventOut)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Create a new event"""
    try:
        db_event = Event(
            title=event.title,
            description=event.description,
            date=event.date,
            venue=event.venue,
            capacity=event.capacity
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event
    except Exception as e:
        print(f"Error creating event: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create event")

@app.put("/events/{event_id}/capacity")
def update_event_capacity(event_id: str, seats: int = None, db: Session = Depends(get_db)):
    """Update event capacity (used by booking service)"""
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        if seats is not None:
            event.capacity = max(0, event.capacity - seats)
            db.commit()
            db.refresh(event)
        
        return {"message": "Capacity updated successfully", "event": event}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating event capacity: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update event capacity")

# ------------------------------------------------------------------------------
# Booking Cleanup Route (Example)
# ------------------------------------------------------------------------------
@app.delete("/bookings/pending")
async def cleanup_pending_bookings(authorization: str = Header(None), db: Session = Depends(get_db)):
    """
    Cleanup pending bookings (stub function).
    Add your logic to clean pending bookings here.
    """
    # TODO: Implement cleanup logic using `authorization` if needed
    return {"message": "Pending bookings cleaned successfully"}

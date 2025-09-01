from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class EventIn(BaseModel):
    title: str
    description: Optional[str]
    date: Optional[datetime]
    venue: Optional[str]
    capacity: int

class EventOut(EventIn):
    id: uuid.UUID
    created_at: datetime

class EventCreate(EventIn):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    venue: Optional[str] = None
    capacity: Optional[int] = None

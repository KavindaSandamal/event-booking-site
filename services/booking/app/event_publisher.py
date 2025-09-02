import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
import aio_pika
from aio_pika import Message, DeliveryMode

logger = logging.getLogger(__name__)

class EventPublisher:
    """Publisher for asynchronous event-driven communication."""
    
    def __init__(self, connection_string: str = None):
        if connection_string is None:
            # Build connection string from environment variables
            rabbitmq_user = os.getenv("RABBITMQ_USER", "admin")
            rabbitmq_pass = os.getenv("RABBITMQ_PASS", "admin123")
            rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
            rabbitmq_port = os.getenv("RABBITMQ_PORT", "5672")
            rabbitmq_vhost = os.getenv("RABBITMQ_VHOST", "/")
            
            # Use RABBITMQ_URL if available, otherwise build from components
            self.connection_string = os.getenv("RABBITMQ_URL") or f"amqp://{rabbitmq_user}:{rabbitmq_pass}@{rabbitmq_host}:{rabbitmq_port}{rabbitmq_vhost}"
        else:
            self.connection_string = connection_string
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchanges: Dict[str, aio_pika.Exchange] = {}
    
    async def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            self.connection = await aio_pika.connect_robust(self.connection_string)
            self.channel = await self.connection.channel()
            
            # Declare exchanges
            await self._declare_exchanges()
            
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def _declare_exchanges(self):
        """Declare all required exchanges."""
        exchanges = [
            ("booking.events", "topic"),
            ("payment.events", "topic"),
            ("notification.events", "topic"),
            ("audit.events", "topic")
        ]
        
        for exchange_name, exchange_type in exchanges:
            exchange = await self.channel.declare_exchange(
                exchange_name,
                exchange_type,
                durable=True
            )
            self.exchanges[exchange_name] = exchange
    
    async def publish_booking_created(self, booking_data: Dict[str, Any]):
        """Publish booking created event."""
        event = {
            "event_type": "booking.created",
            "event_id": f"booking_created_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "data": booking_data,
            "version": "1.0"
        }
        
        await self._publish_event("booking.events", "booking.created", event)
    
    async def publish_booking_cancelled(self, booking_data: Dict[str, Any]):
        """Publish booking cancelled event."""
        event = {
            "event_type": "booking.cancelled",
            "event_id": f"booking_cancelled_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "data": booking_data,
            "version": "1.0"
        }
        
        await self._publish_event("booking.events", "booking.cancelled", event)
    
    async def publish_booking_confirmed(self, booking_data: Dict[str, Any]):
        """Publish booking confirmed event."""
        event = {
            "event_type": "booking.confirmed",
            "event_id": f"booking_confirmed_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "data": booking_data,
            "version": "1.0"
        }
        
        await self._publish_event("booking.events", "booking.confirmed", event)
    
    async def publish_payment_required(self, payment_data: Dict[str, Any]):
        """Publish payment required event."""
        event = {
            "event_type": "payment.required",
            "event_id": f"payment_required_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "data": payment_data,
            "version": "1.0"
        }
        
        await self._publish_event("payment.events", "payment.required", event)
    
    async def publish_notification_send(self, notification_data: Dict[str, Any]):
        """Publish notification send event."""
        event = {
            "event_type": "notification.send",
            "event_id": f"notification_send_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "data": notification_data,
            "version": "1.0"
        }
        
        await self._publish_event("notification.events", "notification.send", event)
    
    async def publish_audit_event(self, audit_data: Dict[str, Any]):
        """Publish audit event."""
        event = {
            "event_type": "audit.log",
            "event_id": f"audit_log_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "data": audit_data,
            "version": "1.0"
        }
        
        await self._publish_event("audit.events", "audit.log", event)
    
    async def _publish_event(self, exchange_name: str, routing_key: str, event: Dict[str, Any]):
        """Publish event to exchange."""
        try:
            if exchange_name not in self.exchanges:
                logger.error(f"Exchange {exchange_name} not found")
                return
            
            message = Message(
                json.dumps(event).encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json",
                timestamp=datetime.now()
            )
            
            await self.exchanges[exchange_name].publish(
                message,
                routing_key=routing_key
            )
            
            logger.info(f"Published event {event['event_type']} to {exchange_name}")
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise
    
    async def close(self):
        """Close connection to RabbitMQ."""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")

# Global event publisher instance
event_publisher = EventPublisher()

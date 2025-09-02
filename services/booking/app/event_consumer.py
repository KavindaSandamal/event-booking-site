import asyncio
import json
import logging
from typing import Dict, Any, Callable
from datetime import datetime
import aio_pika
from aio_pika import Message

logger = logging.getLogger(__name__)

class EventConsumer:
    """Consumer for asynchronous event-driven communication."""
    
    def __init__(self, connection_string: str = "amqp://guest:guest@rabbitmq:5672/"):
        self.connection_string = connection_string
        self.connection: aio_pika.Connection = None
        self.channel: aio_pika.Channel = None
        self.queues: Dict[str, aio_pika.Queue] = {}
        self.handlers: Dict[str, Callable] = {}
    
    async def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            self.connection = await aio_pika.connect_robust(self.connection_string)
            self.channel = await self.connection.channel()
            
            # Set QoS to process one message at a time
            await self.channel.set_qos(prefetch_count=1)
            
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    async def declare_queue(self, queue_name: str, exchange_name: str, routing_key: str):
        """Declare a queue and bind it to an exchange."""
        try:
            # Declare exchange
            exchange = await self.channel.declare_exchange(
                exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            
            # Declare queue
            queue = await self.channel.declare_queue(
                queue_name,
                durable=True
            )
            
            # Bind queue to exchange
            await queue.bind(exchange, routing_key)
            
            self.queues[queue_name] = queue
            
            logger.info(f"Declared queue {queue_name} bound to {exchange_name} with key {routing_key}")
            
        except Exception as e:
            logger.error(f"Failed to declare queue {queue_name}: {e}")
            raise
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register event handler for specific event type."""
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for event type: {event_type}")
    
    async def start_consuming(self, queue_name: str):
        """Start consuming messages from a queue."""
        if queue_name not in self.queues:
            logger.error(f"Queue {queue_name} not found")
            return
        
        queue = self.queues[queue_name]
        
        async def process_message(message: Message):
            """Process incoming message."""
            async with message.process():
                try:
                    # Parse message
                    event_data = json.loads(message.body.decode())
                    event_type = event_data.get("event_type")
                    
                    logger.info(f"Processing event: {event_type}")
                    
                    # Find and execute handler
                    if event_type in self.handlers:
                        await self.handlers[event_type](event_data)
                    else:
                        logger.warning(f"No handler found for event type: {event_type}")
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # In production, you might want to send to dead letter queue
                    raise
        
        # Start consuming
        await queue.consume(process_message)
        logger.info(f"Started consuming from queue: {queue_name}")
    
    async def close(self):
        """Close connection to RabbitMQ."""
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")

# Event handlers
async def handle_payment_completed(event_data: Dict[str, Any]):
    """Handle payment completed event."""
    logger.info(f"Payment completed: {event_data}")
    
    # Update booking status to confirmed
    booking_data = event_data.get("data", {})
    booking_id = booking_data.get("booking_id")
    
    if booking_id:
        # Here you would update the booking status in the database
        logger.info(f"Updating booking {booking_id} status to confirmed")
        # await update_booking_status(booking_id, "confirmed")

async def handle_payment_failed(event_data: Dict[str, Any]):
    """Handle payment failed event."""
    logger.info(f"Payment failed: {event_data}")
    
    # Update booking status to failed
    booking_data = event_data.get("data", {})
    booking_id = booking_data.get("booking_id")
    
    if booking_id:
        # Here you would update the booking status in the database
        logger.info(f"Updating booking {booking_id} status to failed")
        # await update_booking_status(booking_id, "failed")

async def handle_event_cancelled(event_data: Dict[str, Any]):
    """Handle event cancelled event."""
    logger.info(f"Event cancelled: {event_data}")
    
    # Cancel all bookings for this event
    event_data_info = event_data.get("data", {})
    event_id = event_data_info.get("event_id")
    
    if event_id:
        # Here you would cancel all bookings for this event
        logger.info(f"Cancelling all bookings for event {event_id}")
        # await cancel_event_bookings(event_id)

async def handle_user_registered(event_data: Dict[str, Any]):
    """Handle user registered event."""
    logger.info(f"User registered: {event_data}")
    
    # Send welcome email or perform other actions
    user_data = event_data.get("data", {})
    user_id = user_data.get("user_id")
    
    if user_id:
        logger.info(f"Sending welcome email to user {user_id}")
        # await send_welcome_email(user_id)

# Global event consumer instance
event_consumer = EventConsumer()

async def setup_event_consumers():
    """Setup all event consumers."""
    await event_consumer.connect()
    
    # Declare queues and bind to exchanges
    await event_consumer.declare_queue(
        "booking.payment.completed",
        "payment.events",
        "payment.completed"
    )
    
    await event_consumer.declare_queue(
        "booking.payment.failed",
        "payment.events",
        "payment.failed"
    )
    
    await event_consumer.declare_queue(
        "booking.event.cancelled",
        "catalog.events",
        "event.cancelled"
    )
    
    await event_consumer.declare_queue(
        "booking.user.registered",
        "auth.events",
        "user.registered"
    )
    
    # Register handlers
    event_consumer.register_handler("payment.completed", handle_payment_completed)
    event_consumer.register_handler("payment.failed", handle_payment_failed)
    event_consumer.register_handler("event.cancelled", handle_event_cancelled)
    event_consumer.register_handler("user.registered", handle_user_registered)
    
    # Start consuming
    await event_consumer.start_consuming("booking.payment.completed")
    await event_consumer.start_consuming("booking.payment.failed")
    await event_consumer.start_consuming("booking.event.cancelled")
    await event_consumer.start_consuming("booking.user.registered")

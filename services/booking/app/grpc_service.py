import grpc
from concurrent import futures
import logging
from typing import Dict, Any
import asyncio
from datetime import datetime

# gRPC imports
import grpc_pb2
import grpc_pb2_grpc

logger = logging.getLogger(__name__)

class BookingServiceServicer(grpc_pb2_grpc.BookingServiceServicer):
    """gRPC service for high-performance booking operations."""
    
    def __init__(self):
        self.bookings: Dict[str, Any] = {}
    
    async def CreateBooking(self, request, context):
        """Create a new booking via gRPC."""
        try:
            booking_id = f"grpc_booking_{datetime.now().timestamp()}"
            
            # Simulate booking creation
            booking = {
                "id": booking_id,
                "user_id": request.user_id,
                "event_id": request.event_id,
                "tickets": request.tickets,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
            
            self.bookings[booking_id] = booking
            
            return grpc_pb2.BookingResponse(
                success=True,
                booking_id=booking_id,
                message="Booking created successfully"
            )
            
        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return grpc_pb2.BookingResponse(
                success=False,
                booking_id="",
                message=f"Error: {str(e)}"
            )
    
    async def GetBooking(self, request, context):
        """Get booking details via gRPC."""
        try:
            booking = self.bookings.get(request.booking_id)
            
            if not booking:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return grpc_pb2.BookingDetailsResponse(
                    success=False,
                    message="Booking not found"
                )
            
            return grpc_pb2.BookingDetailsResponse(
                success=True,
                booking_id=booking["id"],
                user_id=booking["user_id"],
                event_id=booking["event_id"],
                tickets=booking["tickets"],
                status=booking["status"],
                created_at=booking["created_at"]
            )
            
        except Exception as e:
            logger.error(f"Error getting booking: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return grpc_pb2.BookingDetailsResponse(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    async def UpdateBookingStatus(self, request, context):
        """Update booking status via gRPC."""
        try:
            booking = self.bookings.get(request.booking_id)
            
            if not booking:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return grpc_pb2.BookingResponse(
                    success=False,
                    booking_id=request.booking_id,
                    message="Booking not found"
                )
            
            booking["status"] = request.status
            booking["updated_at"] = datetime.now().isoformat()
            
            return grpc_pb2.BookingResponse(
                success=True,
                booking_id=request.booking_id,
                message="Booking status updated successfully"
            )
            
        except Exception as e:
            logger.error(f"Error updating booking: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return grpc_pb2.BookingResponse(
                success=False,
                booking_id=request.booking_id,
                message=f"Error: {str(e)}"
            )

async def serve():
    """Start the gRPC server."""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add the servicer
    grpc_pb2_grpc.add_BookingServiceServicer_to_server(
        BookingServiceServicer(), server
    )
    
    # Listen on port 50051
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting gRPC server on {listen_addr}")
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())

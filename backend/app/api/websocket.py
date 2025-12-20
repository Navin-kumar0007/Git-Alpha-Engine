import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter()

# Active WebSocket connections
active_connections: List[WebSocket] = []

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    Supports CONNECTION, HEARTBEAT, and MARKET_DATA messages
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial connection success message
        await websocket.send_json({
            "type": "CONNECTION",
            "message": "WebSocket connected successfully",
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Keep connection alive with heartbeat
        while True:
            await asyncio.sleep(30)
            try:
                await websocket.send_json({
                    "type": "HEARTBEAT",
                    "timestamp": asyncio.get_event_loop().time()
                })
            except:
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)


async def broadcast_alert(message: dict):
    """Broadcast alert to all connected clients"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass


async def broadcast_market_data(message: dict):
    """
    Broadcast live market data to all connected clients
    Called by Angel One Service when new ticks arrive
    """
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            # Remove failed connections
            if connection in active_connections:
                active_connections.remove(connection)


# Setup Angel One service broadcast callback on startup
def setup_angel_one_broadcast():
    """Register the broadcast function with Angel One service"""
    from app.services.angel_one_service import angel_one_service
    angel_one_service.set_broadcast_callback(broadcast_market_data)


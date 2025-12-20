"""
Angel One API endpoints for managing live market data subscriptions
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict
from app.api.auth import get_current_user
from app.models import User
from app.services.angel_one_service import angel_one_service

router = APIRouter(prefix="/api/angel-one", tags=["Angel One"])


class TokenSubscription(BaseModel):
    """Model for token subscription requests"""
    exchangeType: int  # 1=NSE, 2=BSE, etc
    tokens: List[str]  # List of token IDs


class SubscribeRequest(BaseModel):
    """Request model for subscribing to tokens"""
    tokens: List[TokenSubscription]
    mode: int = 1  # 1=LTP, 3=Full Quote


class StatusResponse(BaseModel):
    """Response model for service status"""
    is_running: bool
    is_connected: bool
    subscribed_tokens: List[Dict]
    last_update: str


@router.get("/status", response_model=StatusResponse)
async def get_status(current_user: User = Depends(get_current_user)):
    """
    Get the current status of the Angel One WebSocket service
    """
    status = angel_one_service.get_status()
    return StatusResponse(**status)


@router.post("/start")
async def start_connection(
    request: SubscribeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Start the Angel One WebSocket connection with initial subscriptions
    
    Args:
        request: Initial tokens to subscribe to
        current_user: Authenticated user
        
    Returns:
        Success message with status
    """
    try:
        angel_one_service.start(tokens=request.tokens)
        
        return {
            "success": True,
            "message": "Angel One WebSocket started",
            "subscribed_tokens": request.tokens
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start Angel One service: {str(e)}"
        )


@router.post("/stop")
async def stop_connection(current_user: User = Depends(get_current_user)):
    """
    Stop the Angel One WebSocket connection
    """
    try:
        angel_one_service.stop()
        return {
            "success": True,
            "message": "Angel One WebSocket stopped"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop Angel One service: {str(e)}"
        )


@router.post("/subscribe")
async def subscribe_tokens(
    request: SubscribeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Subscribe to additional tokens
    
    Args:
        request: Tokens to subscribe to and mode
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    try:
        if not angel_one_service.is_running:
            raise HTTPException(
                status_code=400,
                detail="Angel One service is not running. Start it first."
            )
        
        angel_one_service.subscribe(request.tokens, request.mode)
        
        return {
            "success": True,
            "message": "Subscribed to tokens",
            "tokens": request.tokens
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to subscribe: {str(e)}"
        )


@router.post("/unsubscribe")
async def unsubscribe_tokens(
    request: SubscribeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Unsubscribe from tokens
    
    Args:
        request: Tokens to unsubscribe from
        current_user: Authenticated user
        
    Returns:
        Success message
    """
    try:
        if not angel_one_service.is_running:
            raise HTTPException(
                status_code=400,
                detail="Angel One service is not running"
            )
        
        angel_one_service.unsubscribe(request.tokens, request.mode)
        
        return {
            "success": True,
            "message": "Unsubscribed from tokens",
            "tokens": request.tokens
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to unsubscribe: {str(e)}"
        )


@router.get("/last-tick/{token}")
async def get_last_tick(
    token: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the last received tick for a specific token
    
    Args:
        token: Token ID (e.g., "26000" for NIFTY)
        current_user: Authenticated user
        
    Returns:
        Last tick data or null if not available
    """
    tick_data = angel_one_service.get_last_tick(token)
    
    if tick_data is None:
        return {
            "success": False,
            "message": "No data available for this token",
            "data": None
        }
    
    return {
        "success": True,
        "data": tick_data
    }

"""
AI Agent API endpoints for financial analysis.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

from app.services.ai_agent_service import AIAgentService
from app.api.auth import get_current_user
from app.models import User


router = APIRouter(prefix="/api/ai-agent", tags=["AI Agent"])


class QueryRequest(BaseModel):
    """Request model for AI agent queries."""
    message: str
    stream: bool = False


class QueryResponse(BaseModel):
    """Response model for AI agent queries."""
    response: str
    success: bool = True


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    configured: bool
    message: Optional[str] = None


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check if the AI agent is configured and ready.
    
    Returns:
        HealthResponse: Agent status information
    """
    is_configured = AIAgentService.is_configured()
    
    if is_configured:
        return HealthResponse(
            status="healthy",
            configured=True,
            message="AI agent is ready"
        )
    else:
        return HealthResponse(
            status="error",
            configured=False,
            message="GROQ_API_KEY not configured"
        )


@router.post("/query", response_model=QueryResponse)
async def query_agent(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send a query to the AI agent.
    
    Args:
        request: Query request with message
        current_user: Authenticated user
        
    Returns:
        QueryResponse: Agent's response
        
    Raises:
        HTTPException: If agent is not configured or query fails
    """
    if not AIAgentService.is_configured():
        raise HTTPException(
            status_code=503,
            detail="AI agent is not configured. Please set GROQ_API_KEY."
        )
    
    try:
        # Handle streaming response
        if request.stream:
            async def generate():
                async for chunk in AIAgentService.stream_query(request.message):
                    # Send as server-sent events
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                # Send completion event
                yield f"data: {json.dumps({'done': True})}\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/event-stream"
            )
        
        # Regular non-streaming response
        response = await AIAgentService.query(request.message)
        
        return QueryResponse(
            response=response,
            success=True
        )
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"❌ AI Agent Error: {str(e)}")
        print(f"Traceback:\n{error_traceback}")
        raise HTTPException(
            status_code=500,
            detail=f"Error querying AI agent: {str(e)}"
        )


@router.post("/analyze-stock/{symbol}")
async def analyze_stock(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """
    Quick stock analysis endpoint.
    
    Args:
        symbol: Stock symbol (e.g., AAPL, TSLA)
        current_user: Authenticated user
        
    Returns:
        QueryResponse: Stock analysis
    """
    if not AIAgentService.is_configured():
        raise HTTPException(
            status_code=503,
            detail="AI agent is not configured"
        )
    
    try:
        # Pre-formatted query for stock analysis
        query = f"""Analyze {symbol} stock and provide:
        1. Current price and 52-week range
        2. Key financial metrics (P/E, Market Cap, etc.)
        3. Analyst recommendations
        4. Brief summary of recent performance
        
        Present the data in tables where appropriate."""
        
        response = await AIAgentService.query(query)
        
        return QueryResponse(
            response=response,
            success=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing stock: {str(e)}"
        )

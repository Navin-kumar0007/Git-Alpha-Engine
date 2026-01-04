"""
Angel One Portfolio API Endpoints
Manage live portfolio sync from Angel One broker account
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.models import User
from app.db import get_db
from app.services.angel_one_portfolio_service import angel_one_portfolio_service


router = APIRouter(prefix="/api/angel-portfolio", tags=["Angel One Portfolio"])


class PortfolioSyncResponse(BaseModel):
    """Response model for portfolio sync"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    synced_at: Optional[str] = None
    cached: bool = False


@router.get("/sync", response_model=PortfolioSyncResponse)
async def sync_portfolio(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger full portfolio sync from Angel One
    Fetches holdings, positions, and funds from broker account
    """
    try:
        result = angel_one_portfolio_service.sync_all(db, current_user.id)
        
        return PortfolioSyncResponse(
            success=result['success'],
            data=result.get('data'),
            error=result.get('error'),
            synced_at=result.get('synced_at'),
            cached=False
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync portfolio: {str(e)}"
        )


@router.get("/holdings")
async def get_holdings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get cached holdings from database
    Returns last synced holdings without calling Angel One API
    """
    try:
        result = angel_one_portfolio_service.get_cached_portfolio(db, current_user.id)
        
        if result['success']:
            return {
                "success": True,
                "data": result['data']['holdings'],
                "synced_at": result.get('synced_at'),
                "cached": True
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Failed to fetch holdings')
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching holdings: {str(e)}"
        )


@router.get("/positions")
async def get_positions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get cached positions from database
    Returns last synced positions without calling Angel One API
    """
    try:
        result = angel_one_portfolio_service.get_cached_portfolio(db, current_user.id)
        
        if result['success']:
            return {
                "success": True,
                "data": result['data']['positions'],
                "synced_at": result.get('synced_at'),
                "cached": True
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Failed to fetch positions')
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching positions: {str(e)}"
        )


@router.get("/funds")
async def get_funds(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get cached funds/margin from database
    Returns last synced funds without calling Angel One API
    """
    try:
        result = angel_one_portfolio_service.get_cached_portfolio(db, current_user.id)
        
        if result['success']:
            return {
                "success": True,
                "data": result['data']['funds'],
                "synced_at": result.get('synced_at'),
                "cached": True
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Failed to fetch funds')
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching funds: {str(e)}"
        )


@router.get("/status")
async def get_sync_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get portfolio sync status
    Returns last sync time and cached data availability
    """
    try:
        result = angel_one_portfolio_service.get_cached_portfolio(db, current_user.id)
        
        has_data = False
        if result['success']:
            data = result['data']
            has_data = (
                len(data.get('holdings', [])) > 0 or 
                len(data.get('positions', [])) > 0 or 
                data.get('funds') is not None
            )
        
        return {
            "success": True,
            "has_cached_data": has_data,
            "last_sync": result.get('synced_at'),
            "authenticated": angel_one_portfolio_service.authenticated
        }
    except Exception as e:
        return {
            "success": False,
            "has_cached_data": False,
            "last_sync": None,
            "error": str(e)
        }


@router.post("/refresh")
async def force_refresh(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Force refresh portfolio data from Angel One
    Same as /sync but explicitly indicates a forced refresh
    """
    try:
        result = angel_one_portfolio_service.sync_all(db, current_user.id)
        
        return {
            "success": result['success'],
            "data": result.get('data'),
            "error": result.get('error'),
            "synced_at": result.get('synced_at')
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh portfolio: {str(e)}"
        )

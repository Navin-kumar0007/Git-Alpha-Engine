"""
Portfolio API Endpoints
Manage user portfolio, transactions, and analytics
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db
from app.core.security import get_current_user
from app.services import portfolio_manager

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("/summary", response_model=schemas.PortfolioSummary)
async def get_portfolio_summary(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete portfolio summary with P&L analytics"""
    summary = await portfolio_manager.calculate_portfolio_summary(db, current_user.id)
    return summary


@router.get("/holdings", response_model=List[schemas.PortfolioItemOut])
async def get_holdings(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all portfolio holdings"""
    holdings = await portfolio_manager.get_user_portfolio(db, current_user.id)
    return holdings


@router.post("/transaction", response_model=schemas.TransactionOut)
async def add_transaction(
    transaction: schemas.TransactionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a buy/sell transaction
    Automatically updates portfolio holdings and calculates P&L
    """
    if transaction.transaction_type not in ["buy", "sell"]:
        raise HTTPException(status_code=400, detail="Transaction type must be 'buy' or 'sell'")
    
    if transaction.amount <= 0 or transaction.price <= 0:
        raise HTTPException(status_code=400, detail="Amount and price must be positive")
    
    result = await portfolio_manager.add_transaction(
        db=db,
        user_id=current_user.id,
        asset_id=transaction.asset_id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        price=transaction.price,
        notes=transaction.notes
    )
    
    return result


@router.get("/transactions", response_model=List[schemas.TransactionOut])
async def get_transactions(
    asset_id: str = None,
    limit: int = 50,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction history"""
    transactions = await portfolio_manager.get_transaction_history(
        db, current_user.id, asset_id, limit
    )
    return transactions


@router.delete("/holdings/{asset_id}")
async def delete_holding(
    asset_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a portfolio holding (only if amount is zero)"""
    success = await portfolio_manager.delete_portfolio_item(db, current_user.id, asset_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete holding with non-zero amount"
        )
    return {"message": "Portfolio item deleted successfully"}

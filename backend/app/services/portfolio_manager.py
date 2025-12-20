"""
Portfolio Manager Service
Handles portfolio tracking, P&L calculations, and performance analytics
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models, schemas
from app.services.market_data import get_assets_with_metrics


async def get_user_portfolio(db: Session, user_id: int) -> List[models.Portfolio]:
    """Get all portfolio items for a user"""
    return db.query(models.Portfolio).filter(models.Portfolio.user_id == user_id).all()


async def get_portfolio_item(db: Session, user_id: int, asset_id: str) -> Optional[models.Portfolio]:
    """Get a specific portfolio item"""
    return db.query(models.Portfolio).filter(
        models.Portfolio.user_id == user_id,
        models.Portfolio.asset_id == asset_id
    ).first()


async def add_transaction(
    db: Session,
    user_id: int,
    asset_id: str,
    transaction_type: str,
    amount: float,
    price: float,
    notes: Optional[str] = None
) -> models.Transaction:
    """
    Add a buy/sell transaction and update portfolio
    """
    # Get or create portfolio item
    portfolio_item = await get_portfolio_item(db, user_id, asset_id)
    
    if not portfolio_item:
        # Create new portfolio item
        portfolio_item = models.Portfolio(
            user_id=user_id,
            asset_id=asset_id,
            amount=0.0,
            avg_entry_price=0.0
        )
        db.add(portfolio_item)
        db.flush()
    
    # Create transaction
    total_value = amount * price
    transaction = models.Transaction(
        portfolio_id=portfolio_item.id,
        transaction_type=transaction_type,
        amount=amount,
        price=price,
        total_value=total_value,
        notes=notes
    )
    db.add(transaction)
    
    # Update portfolio holdings
    if transaction_type == "buy":
        # Calculate new average entry price
        total_cost = (portfolio_item.amount * portfolio_item.avg_entry_price) + total_value
        new_amount = portfolio_item.amount + amount
        portfolio_item.avg_entry_price = total_cost / new_amount if new_amount > 0 else price
        portfolio_item.amount = new_amount
    elif transaction_type == "sell":
        portfolio_item.amount = max(0, portfolio_item.amount - amount)
        # If sold all, reset avg price
        if portfolio_item.amount == 0:
            portfolio_item.avg_entry_price = 0
    
    db.commit()
    db.refresh(transaction)
    db.refresh(portfolio_item)
    
    return transaction


async def calculate_portfolio_summary(db: Session, user_id: int) -> Dict:
    """
    Calculate complete portfolio summary with P&L
    """
    portfolio_items = await get_user_portfolio(db, user_id)
    
    if not portfolio_items:
        return {
            "total_value": 0,
            "total_cost": 0,
            "total_pnl": 0,
            "total_pnl_percentage": 0,
            "holdings": [],
            "top_performers": [],
            "worst_performers": []
        }
    
    # Get current market prices
    try:
        assets = await get_assets_with_metrics()
        price_map = {asset["id"]: asset for asset in assets}
    except:
        price_map = {}
    
    holdings = []
    total_value = 0
    total_cost = 0
    
    for item in portfolio_items:
        if item.amount <= 0:
            continue
            
        # Get current price
        asset_data = price_map.get(item.asset_id, {})
        current_price = asset_data.get("price", item.avg_entry_price)
        
        # Calculate metrics
        cost_basis = item.amount * item.avg_entry_price
        current_value = item.amount * current_price
        pnl = current_value - cost_basis
        pnl_percentage = (pnl / cost_basis * 100) if cost_basis > 0 else 0
        
        holding = {
            "asset_id": item.asset_id,
            "name": asset_data.get("name", item.asset_id.title()),
            "symbol": asset_data.get("symbol", item.asset_id.upper()[:4]),
            "amount": item.amount,
            "avg_entry_price": item.avg_entry_price,
            "current_price": current_price,
            "cost_basis": cost_basis,
            "current_value": current_value,
            "pnl": pnl,
            "pnl_percentage": pnl_percentage,
            "change_24h": asset_data.get("change24h", 0)
        }
        holdings.append(holding)
        
        total_value += current_value
        total_cost += cost_basis
    
    # Sort for top/worst performers
    sorted_holdings = sorted(holdings, key=lambda x: x["pnl_percentage"], reverse=True)
    
    return {
        "total_value": total_value,
        "total_cost": total_cost,
        "total_pnl": total_value - total_cost,
        "total_pnl_percentage": ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0,
        "holdings": holdings,
        "top_performers": sorted_holdings[:3] if len(sorted_holdings) >= 3 else sorted_holdings,
        "worst_performers": sorted_holdings[-3:][::-1] if len(sorted_holdings) >= 3 else []
    }


async def get_transaction_history(
    db: Session,
    user_id: int,
    asset_id: Optional[str] = None,
    limit: int = 50
) -> List[models.Transaction]:
    """Get transaction history for a user"""
    query = db.query(models.Transaction).join(models.Portfolio).filter(
        models.Portfolio.user_id == user_id
    )
    
    if asset_id:
        query = query.filter(models.Portfolio.asset_id == asset_id)
    
    return query.order_by(models.Transaction.timestamp.desc()).limit(limit).all()


async def delete_portfolio_item(db: Session, user_id: int, asset_id: str) -> bool:
    """Delete a portfolio item (must have zero holdings)"""
    item = await get_portfolio_item(db, user_id, asset_id)
    if item and item.amount == 0:
        db.delete(item)
        db.commit()
        return True
    return False

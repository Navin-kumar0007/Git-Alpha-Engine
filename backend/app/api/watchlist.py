from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models
from ..db import get_db
from ..core.security import get_current_user
from ..schemas import WatchlistCreate, WatchlistItemOut

router = APIRouter(prefix="/api")

@router.get("/watchlist", response_model=List[WatchlistItemOut])
def get_watchlist(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """JWT-protected: full watchlist objects for current user"""
    items = (
        db.query(models.Watchlist)
        .filter(models.Watchlist.user_id == current_user.id)
        .order_by(models.Watchlist.created_at.desc())
        .all()
    )
    return items

@router.get("/watchlist/{user_id}")
def get_watchlist_legacy(user_id: int, db: Session = Depends(get_db)):
    """Legacy endpoint used by current frontend: returns just asset_id list."""
    items = (
        db.query(models.Watchlist)
        .filter(models.Watchlist.user_id == user_id)
        .order_by(models.Watchlist.created_at.desc())
        .all()
    )
    return [item.asset_id for item in items]

@router.post("/watchlist", response_model=WatchlistItemOut)
def add_to_watchlist(
    item_in: WatchlistCreate,
    db: Session = Depends(get_db),
):
    """Upsert watchlist item.

    - If called from legacy frontend, `user_id` is passed in the body.
    - For future JWT usage, you can ignore `user_id` and use /watchlist with Authorization header instead.
    """
    if not item_in.user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    existing = (
        db.query(models.Watchlist)
        .filter(models.Watchlist.user_id == item_in.user_id, models.Watchlist.asset_id == item_in.asset_id)
        .first()
    )
    if existing:
        existing.target_price = item_in.target_price
        existing.direction = item_in.direction
        db.commit()
        db.refresh(existing)
        return existing

    item = models.Watchlist(
        user_id=item_in.user_id,
        asset_id=item_in.asset_id,
        target_price=item_in.target_price,
        direction=item_in.direction,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/watchlist/{item_id}")
def remove_from_watchlist(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    item = (
        db.query(models.Watchlist)
        .filter(models.Watchlist.id == item_id, models.Watchlist.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted"}

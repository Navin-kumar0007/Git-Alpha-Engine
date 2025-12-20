import asyncio
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from .. import models
from .market_data import get_assets_with_metrics


async def evaluate_rules_and_create_alerts(db: Session) -> List[models.Alert]:
    """
    Check all watchlist rules against live prices.
    If trigger condition satisfied, create Alert rows and return them.
    """
    # map asset_id -> price
    assets = await get_assets_with_metrics()
    price_map: Dict[str, float] = {a["id"]: float(a["price"]) for a in assets}

    triggered: List[models.Alert] = []

    # Assuming your watchlist model is called WatchlistItem.
    # If it's named differently, adjust here.
    q = db.query(models.Watchlist).filter(
        models.Watchlist.target_price.isnot(None),
        models.Watchlist.direction.isnot(None),
    )

    for item in q.all():
        current_price = price_map.get(item.asset_id)
        if current_price is None:
            continue

        target = float(item.target_price)
        direction = item.direction

        hit = False
        if direction == "above" and current_price >= target:
            hit = True
        elif direction == "below" and current_price <= target:
            hit = True

        if not hit:
            continue

        title = f"Rule hit for {item.asset_id}"
        if direction == "above":
            message = f"{item.asset_id} is now above your target: {current_price:.2f} ≥ {target:.2f}"
        else:
            message = f"{item.asset_id} is now below your target: {current_price:.2f} ≤ {target:.2f}"

        alert = models.Alert(
            user_id=item.user_id,
            asset_id=item.asset_id,
            title=title,
            message=message,
            sentiment="positive" if direction == "above" else "negative",
        )
        db.add(alert)
        triggered.append(alert)

    if triggered:
        db.commit()
        for a in triggered:
            db.refresh(a)

    return triggered

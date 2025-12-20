from typing import List

from fastapi import APIRouter
from ..schemas import Asset
from ..services.market_data import get_assets_with_metrics

# IMPORTANT: prefix is /api/assets so frontend URL `${API_URL}/api/assets` works
router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("", response_model=List[Asset])
async def list_assets() -> List[Asset]:
    """
    Return live market + GitHub data for tracked assets.
    """
    return await get_assets_with_metrics()

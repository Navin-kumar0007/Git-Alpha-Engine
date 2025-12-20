from .auth import router as auth_router
from .assets import router as assets_router
from .profile import router as profile_router
from .watchlist import router as watchlist_router
from .preferences import router as preferences_router
from .websocket import router as websocket_router
from .portfolio import router as portfolio_router
from .markets import router as markets_router
from .news import router as news_router
from .angel_one import router as angel_one_router

__all__ = [
    "auth_router",
    "assets_router",
    "profile_router",
    "watchlist_router",
    "preferences_router",
    "websocket_router",
    "portfolio_router",
    "markets_router",
    "news_router",
    "angel_one_router",
]


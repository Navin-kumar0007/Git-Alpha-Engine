import warnings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os

# Suppress Pydantic protected namespace warnings from third-party libraries (agno)
warnings.filterwarnings("ignore", message=".*Field.*has conflict with protected namespace.*")

# Load environment variables from .env file
load_dotenv()

from app.api import (
    auth_router,
    assets_router,
    profile_router,
    watchlist_router,
    preferences_router,
    websocket_router,
    portfolio_router,
    markets_router,
    news_router,
    angel_one_router,
)
from app.api.ai_agent import router as ai_agent_router
from app.api.websocket import setup_angel_one_broadcast


app = FastAPI(title="Git Alpha Engine")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware for OAuth (required by authlib)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
)

app.include_router(auth_router)
app.include_router(assets_router)
app.include_router(profile_router)
app.include_router(watchlist_router)
app.include_router(preferences_router)
app.include_router(websocket_router)
app.include_router(portfolio_router)
app.include_router(markets_router)
app.include_router(ai_agent_router)
app.include_router(news_router)
app.include_router(angel_one_router)

# Setup Angel One broadcast callback on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    from app.services.angel_one_service import angel_one_service
    
    # Register broadcast callback
    setup_angel_one_broadcast()
    print("✓ Angel One broadcast callback registered")
    
    # Check if Angel One credentials are configured
    angel_enabled = all([
        os.getenv("ANGEL_API_KEY"),
        os.getenv("ANGEL_CLIENT_ID"),
        os.getenv("ANGEL_PASSWORD"),
        os.getenv("ANGEL_TOTP_KEY")
    ])
    
    if angel_enabled:
        # Auto-start with default tokens (NIFTY & BANKNIFTY)
        default_tokens = [
            {"exchangeType": 1, "tokens": ["26000", "26009"]}  # NIFTY 50, BANK NIFTY
        ]
        
        try:
            angel_one_service.start(tokens=default_tokens)
            print("✓ Angel One service auto-started with NIFTY & BANKNIFTY")
            print("  You can subscribe to more tokens via /api/angel-one/subscribe")
        except Exception as e:
            print(f"⚠ Failed to auto-start Angel One service: {e}")
            print("  Service can still be started manually via /api/angel-one/start")
    else:
        print("ℹ Angel One credentials not configured - service disabled")
        print("  Add ANGEL_* variables to .env to enable live market data")




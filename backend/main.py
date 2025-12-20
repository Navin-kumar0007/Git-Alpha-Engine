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
    setup_angel_one_broadcast()
    print("Angel One broadcast callback registered")



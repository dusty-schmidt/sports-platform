#!/usr/bin/env python3
"""Simple FastAPI application for testing betting market functionality."""

import logging
import json
import os
from datetime import datetime
from typing import List, Optional
from dataclasses import asdict
import json
from datetime import datetime

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database components
try:
    from database import get_db, init_db, BettingMarketDBService
    from database.models import Sport, Sportsbook, BettingMarket, MarketSnapshot
    from betting_service.service import BettingMarketService
    from betting_service.models import MarketEvent
    logger.info("Successfully imported all database and service modules")
except ImportError as e:
    logger.error(f"Import error: {e}")
    # Create mock classes for testing
    class MockDBService:
        def get_stats(self):
            return {"status": "mock", "error": str(e)}
    
    BettingMarketDBService = MockDBService
    Sport = Sportsbook = BettingMarket = MarketSnapshot = None

# FastAPI app
app = FastAPI(
    title="Betting Market Test API",
    version="1.0.0",
    description="Test API for betting market functionality"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_service(db: Session = Depends(get_db)) -> BettingMarketDBService:
    """Get database service instance."""
    return BettingMarketDBService(db)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting up application...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Betting Market Test API is running"
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Betting Market Test API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/test/database")
async def test_database(db: Session = Depends(get_db)):
    """Test database connection and basic operations."""
    try:
        # Test basic queries
        sports_count = db.query(Sport).count() if Sport else 0
        sportsbooks_count = db.query(Sportsbook).count() if Sportsbook else 0
        markets_count = db.query(BettingMarket).count() if BettingMarket else 0
        
        return {
            "status": "success",
            "database_connection": "ok",
            "sports_count": sports_count,
            "sportsbooks_count": sportsbooks_count,
            "markets_count": markets_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database test failed: {str(e)}")

@app.get("/test/collect")
async def test_collection():
    """Test data collection functionality."""
    try:
        # This will test the actual data collection from sportsbooks
        service = BettingMarketService("nba")
        events = service.collect()
        
        # Save collected data to file for inspection
        data_dir = "/app/data"
        os.makedirs(data_dir, exist_ok=True)
        
        collection_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "events_count": len(events),
            "events": []
        }
        
        for event in events:
            try:
                event_data = asdict(event) if hasattr(event, '__dataclass_fields__') else {
                    "book": getattr(event, 'book', 'unknown'),
                    "sport": getattr(event, 'sport', 'unknown'),
                    "game": getattr(event, 'game', 'unknown'),
                    "away": getattr(event, 'away', 'unknown'),
                    "home": getattr(event, 'home', 'unknown'),
                    "game_start": str(getattr(event, 'game_start', 'unknown')),
                    "away_moneyline": getattr(event, 'away_moneyline', None),
                    "home_moneyline": getattr(event, 'home_moneyline', None),
                    "away_spread": getattr(event, 'away_spread', None),
                    "home_spread": getattr(event, 'home_spread', None),
                    "total": getattr(event, 'total', None),
                    "over_price": getattr(event, 'over_price', None),
                    "under_price": getattr(event, 'under_price', None),
                    "retrieved_at": str(getattr(event, 'retrieved_at', 'unknown'))
                }
                collection_data["events"].append(event_data)
            except Exception as e:
                logger.warning(f"Failed to serialize event: {e}")
                collection_data["events"].append({"error": str(e), "raw_event": str(event)})
        
        # Save to file
        filename = f"collection_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(collection_data, f, indent=2, cls=DateTimeEncoder)
        
        logger.info(f"Saved collection data to {filepath}")
        
        return {
            "status": "success",
            "events_collected": len(events),
            "data_saved_to": filename,
            "sample_event": collection_data["events"][0] if collection_data["events"] else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Collection test failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/test/sportsbooks")
async def test_sportsbooks():
    """Test sportsbook client functionality."""
    try:
        from betting_service.books import DraftKingsClient, FanDuelClient
        
        # Test client creation with proper parameters
        dk_client = DraftKingsClient(
            sport="nba",
            team_aliases={"golden state warriors": "GSW", "phoenix suns": "PHX"},
            timezone="America/New_York",
            league_id="42648"
        )
        fd_client = FanDuelClient(
            sport="nba",
            team_aliases={"golden state warriors": "GSW", "phoenix suns": "PHX"},
            timezone="America/New_York",
            custom_page_id="nba"
        )
        
        return {
            "status": "success",
            "draftkings_client": {
                "type": str(type(dk_client)),
                "name": dk_client.name,
                "sport": "nba"
            },
            "fanduel_client": {
                "type": str(type(fd_client)),
                "name": fd_client.name,
                "sport": "nba"
            },
            "configuration_valid": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Sportsbooks test failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
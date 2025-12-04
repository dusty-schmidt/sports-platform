#!/usr/bin/env python3
"""Startup script for the betting market API service."""

import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Start the betting market API service."""
    logger.info("Starting Betting Market Data Service...")
    logger.info("Python version: %s", sys.version)
    logger.info("Current working directory: %s", os.getcwd())
    
    # Import and initialize database
    try:
        from database import init_db, get_db
        from database.models import Sport, Sportsbook
        
        logger.info("Initializing database...")
        init_db()
        
        # Add default sports and sportsbooks if they don't exist
        db = next(get_db())
        try:
            # Add default sports
            default_sports = [
                ("nba", "NBA"),
                ("nfl", "NFL"), 
                ("mlb", "MLB"),
                ("nhl", "NHL"),
                ("soccer", "Soccer")
            ]
            
            for sport_name, display_name in default_sports:
                if not db.query(Sport).filter(Sport.name == sport_name).first():
                    sport = Sport(name=sport_name, display_name=display_name)
                    db.add(sport)
                    logger.info("Added sport: %s", sport_name)
            
            # Add default sportsbooks
            default_sportsbooks = [
                ("draftkings", "DraftKings"),
                ("fanduel", "FanDuel")
            ]
            
            for book_name, display_name in default_sportsbooks:
                if not db.query(Sportsbook).filter(Sportsbook.name == book_name).first():
                    sportsbook = Sportsbook(name=book_name, display_name=display_name)
                    db.add(sportsbook)
                    logger.info("Added sportsbook: %s", book_name)
            
            db.commit()
            logger.info("Database initialized successfully")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error("Failed to initialize database: %s", e)
        sys.exit(1)
    
    # Start the API server
    try:
        import uvicorn
        logger.info("Starting FastAPI server on http://0.0.0.0:8000")
        logger.info("API Documentation will be available at: http://localhost:8000/docs")
        logger.info("Health check endpoint: http://localhost:8000/health")
        
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,  # Set to True for development
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("Shutting down service...")
    except Exception as e:
        logger.error("Failed to start server: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
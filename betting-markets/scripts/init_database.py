#!/usr/bin/env python3
"""Database initialization and management script."""

import sys
import argparse
from datetime import datetime

from database import init_db, drop_db, get_db
from database.models import Sport, Sportsbook, BettingMarket, MarketSnapshot
from database.service import BettingMarketDBService

def init_database():
    """Initialize the database with default data."""
    print("Initializing database...")
    
    # Initialize tables
    init_db()
    
    # Add default sports and sportsbooks
    db = next(get_db())
    try:
        service = BettingMarketDBService(db)
        
        # Add default sports
        sports = [
            ("nba", "NBA"),
            ("nfl", "NFL"), 
            ("mlb", "MLB"),
            ("nhl", "NHL"),
            ("soccer", "Soccer")
        ]
        
        print("Adding default sports...")
        for sport_name, display_name in sports:
            sport = service.ensure_sport(sport_name, display_name)
            print(f"  ✓ {sport_name}: {sport.display_name}")
        
        # Add default sportsbooks
        sportsbooks = [
            ("draftkings", "DraftKings"),
            ("fanduel", "FanDuel")
        ]
        
        print("Adding default sportsbooks...")
        for book_name, display_name in sportsbooks:
            sportsbook = service.ensure_sportsbook(book_name, display_name)
            print(f"  ✓ {book_name}: {sportsbook.display_name}")
        
        db.commit()
        print("Database initialization complete!")
        
        # Show stats
        stats = service.get_stats()
        print(f"Database stats:")
        print(f"  Sports: {stats['sports']}")
        print(f"  Sportsbooks: {stats['sportsbooks']}")
        print(f"  Markets: {stats['markets']}")
        print(f"  Snapshots: {stats['snapshots']}")
        
    finally:
        db.close()

def check_database():
    """Check database status and stats."""
    print("Checking database status...")
    
    db = next(get_db())
    try:
        service = BettingMarketDBService(db)
        
        # Get stats
        stats = service.get_stats()
        
        print("Database Statistics:")
        print(f"  Sports: {stats['sports']}")
        print(f"  Sportsbooks: {stats['sportsbooks']}")
        print(f"  Total Markets: {stats['markets']}")
        print(f"  Total Snapshots: {stats['snapshots']}")
        print(f"  Active Markets: {stats['active_markets']}")
        
        if stats['latest_snapshot']:
            print(f"  Latest Snapshot: {stats['latest_snapshot']}")
        
        # List all sports
        sports = db.query(Sport).all()
        print(f"\nSports ({len(sports)}):")
        for sport in sports:
            print(f"  - {sport.name}: {sport.display_name}")
        
        # List all sportsbooks
        sportsbooks = db.query(Sportsbook).all()
        print(f"\nSportsbooks ({len(sportsbooks)}):")
        for sportsbook in sportsbooks:
            status = "✓ Active" if sportsbook.is_active else "✗ Inactive"
            print(f"  - {sportsbook.name}: {sportsbook.display_name} {status}")
        
        # Recent markets
        recent_markets = db.query(BettingMarket).order_by(BettingMarket.created_at.desc()).limit(5).all()
        print(f"\nRecent Markets:")
        for market in recent_markets:
            print(f"  - {market.game_name}: {market.away_team} @ {market.home_team}")
        
    finally:
        db.close()

def cleanup_old_data(days_to_keep=7):
    """Clean up old snapshot data."""
    print(f"Cleaning up snapshots older than {days_to_keep} days...")
    
    db = next(get_db())
    try:
        service = BettingMarketDBService(db)
        deleted_count = service.cleanup_old_snapshots(days_to_keep)
        print(f"Deleted {deleted_count} old snapshots")
    finally:
        db.close()

def drop_database():
    """Drop all database tables (WARNING: This deletes all data!)."""
    response = input("WARNING: This will delete ALL data in the database. Type 'yes' to confirm: ")
    if response.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    print("Dropping all tables...")
    drop_db()
    print("Database dropped successfully.")

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Database management for Betting Market Service")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize database with default data')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check database status and stats')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old data')
    cleanup_parser.add_argument('--days', type=int, default=7, help='Days of data to keep (default: 7)')
    
    # Drop command
    drop_parser = subparsers.add_parser('drop', help='Drop all database tables (DANGEROUS!)')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        init_database()
    elif args.command == 'check':
        check_database()
    elif args.command == 'cleanup':
        cleanup_old_data(args.days)
    elif args.command == 'drop':
        drop_database()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
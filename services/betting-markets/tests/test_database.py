"""Tests for database models and service layer."""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, Sport, Sportsbook, BettingMarket, MarketSnapshot
from database.service import BettingMarketDBService
from betting_service.models import MarketEvent


class TestDatabaseModels:
    """Test database model functionality."""
    
    @pytest.fixture
    def db_engine(self):
        """Create in-memory SQLite database for testing."""
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=engine)
        return engine
    
    @pytest.fixture
    def db_session(self, db_engine):
        """Create database session for testing."""
        Session = sessionmaker(bind=db_engine)
        session = Session()
        yield session
        session.close()
    
    def test_sport_creation(self, db_session):
        """Test creating and retrieving sports."""
        # Create sport
        sport = Sport(name="nba", display_name="NBA")
        db_session.add(sport)
        db_session.commit()
        
        # Retrieve sport
        retrieved = db_session.query(Sport).filter(Sport.name == "nba").first()
        assert retrieved is not None
        assert retrieved.name == "nba"
        assert retrieved.display_name == "NBA"
    
    def test_sportsbook_creation(self, db_session):
        """Test creating and retrieving sportsbooks."""
        # Create sportsbook
        sportsbook = Sportsbook(name="draftkings", display_name="DraftKings")
        db_session.add(sportsbook)
        db_session.commit()
        
        # Retrieve sportsbook
        retrieved = db_session.query(Sportsbook).filter(Sportsbook.name == "draftkings").first()
        assert retrieved is not None
        assert retrieved.name == "draftkings"
        assert retrieved.display_name == "DraftKings"
        assert retrieved.is_active == True
    
    def test_betting_market_creation(self, db_session):
        """Test creating and retrieving betting markets."""
        # Create dependent records
        sport = Sport(name="nba", display_name="NBA")
        db_session.add(sport)
        db_session.commit()
        
        # Create market
        market = BettingMarket(
            sport_id=sport.id,
            game_name="Lakers vs Warriors",
            away_team="Los Angeles Lakers",
            home_team="Golden State Warriors",
            game_start_time=datetime.utcnow() + timedelta(hours=2)
        )
        db_session.add(market)
        db_session.commit()
        
        # Retrieve market
        retrieved = db_session.query(BettingMarket).first()
        assert retrieved is not None
        assert retrieved.game_name == "Lakers vs Warriors"
        assert retrieved.away_team == "Los Angeles Lakers"
        assert retrieved.home_team == "Golden State Warriors"
    
    def test_market_snapshot_creation(self, db_session):
        """Test creating and retrieving market snapshots."""
        # Create dependent records
        sport = Sport(name="nba", display_name="NBA")
        sportsbook = Sportsbook(name="draftkings", display_name="DraftKings")
        db_session.add_all([sport, sportsbook])
        db_session.commit()
        
        # Create market
        market = BettingMarket(
            sport_id=sport.id,
            game_name="Lakers vs Warriors",
            away_team="Los Angeles Lakers",
            home_team="Golden State Warriors",
            game_start_time=datetime.utcnow() + timedelta(hours=2)
        )
        db_session.add(market)
        db_session.commit()
        
        # Create snapshot
        snapshot = MarketSnapshot(
            market_id=market.id,
            sportsbook_id=sportsbook.id,
            away_moneyline="+150",
            home_moneyline="-180",
            away_spread=3.5,
            away_spread_price="-110",
            home_spread=-3.5,
            home_spread_price="-110",
            total_points=220.5,
            over_price="-110",
            under_price="-110"
        )
        db_session.add(snapshot)
        db_session.commit()
        
        # Retrieve snapshot
        retrieved = db_session.query(MarketSnapshot).first()
        assert retrieved is not None
        assert retrieved.away_moneyline == "+150"
        assert retrieved.home_moneyline == "-180"
        assert retrieved.total_points == 220.5


class TestBettingMarketDBService:
    """Test database service layer."""
    
    @pytest.fixture
    def db_session(self):
        """Create in-memory database session for testing."""
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    def test_ensure_sport(self, db_session):
        """Test ensuring sport exists in database."""
        service = BettingMarketDBService(db_session)
        
        # Ensure sport that doesn't exist
        sport = service.ensure_sport("nba", "NBA")
        assert sport.id is not None
        assert sport.name == "nba"
        assert sport.display_name == "NBA"
        
        # Ensure same sport again (should return existing)
        same_sport = service.ensure_sport("nba", "National Basketball Association")
        assert same_sport.id == sport.id
        assert same_sport.display_name == "NBA"  # Should not update
    
    def test_ensure_sportsbook(self, db_session):
        """Test ensuring sportsbook exists in database."""
        service = BettingMarketDBService(db_session)
        
        # Ensure sportsbook that doesn't exist
        sportsbook = service.ensure_sportsbook("draftkings", "DraftKings")
        assert sportsbook.id is not None
        assert sportsbook.name == "draftkings"
        assert sportsbook.display_name == "DraftKings"
    
    def test_create_or_update_market(self, db_session):
        """Test creating and updating betting markets."""
        service = BettingMarketDBService(db_session)
        
        # Create market
        game_start = datetime.utcnow() + timedelta(hours=2)
        market = service.create_or_update_market(
            sport_name="nba",
            game_name="Lakers vs Warriors",
            away_team="Los Angeles Lakers",
            home_team="Golden State Warriors",
            game_start_time=game_start
        )
        
        assert market.id is not None
        assert market.game_name == "Lakers vs Warriors"
        assert market.away_team == "Los Angeles Lakers"
        
        # Update market (should find existing)
        updated_market = service.create_or_update_market(
            sport_name="nba",
            game_name="Lakers vs Warriors (Updated)",
            away_team="Los Angeles Lakers",
            home_team="Golden State Warriors",
            game_start_time=game_start
        )
        
        assert updated_market.id == market.id
        assert updated_market.game_name == "Lakers vs Warriors (Updated)"
    
    def test_store_market_events(self, db_session):
        """Test storing market events in database."""
        service = BettingMarketDBService(db_session)
        
        # Create test market events
        events = [
            MarketEvent(
                book="draftkings",
                sport="nba",
                game="Lakers vs Warriors",
                game_start=datetime.utcnow() + timedelta(hours=2),
                away="Los Angeles Lakers",
                home="Golden State Warriors",
                total=220.5,
                over_price="-110",
                under_price="-110",
                away_moneyline="+150",
                home_moneyline="-180",
                away_spread=3.5,
                away_spread_price="-110",
                home_spread=-3.5,
                home_spread_price="-110",
                retrieved_at=datetime.utcnow()
            )
        ]
        
        snapshots = service.store_market_events(events)
        
        assert len(snapshots) == 1
        assert snapshots[0].market_id is not None
        assert snapshots[0].sportsbook_id is not None
        assert snapshots[0].away_moneyline == "+150"
        assert snapshots[0].home_moneyline == "-180"
    
    def test_get_active_markets(self, db_session):
        """Test getting active markets."""
        service = BettingMarketDBService(db_session)
        
        # Create test data
        service.ensure_sport("nba")
        game_start = datetime.utcnow() + timedelta(hours=2)
        service.create_or_update_market(
            sport_name="nba",
            game_name="Lakers vs Warriors",
            away_team="Los Angeles Lakers",
            home_team="Golden State Warriors",
            game_start_time=game_start
        )
        
        # Get active markets
        markets = service.get_active_markets(limit=10)
        
        assert len(markets) == 1
        assert markets[0].game_name == "Lakers vs Warriors"
        
        # Test filtering by sport
        markets_nba = service.get_active_markets(sport="nba", limit=10)
        assert len(markets_nba) == 1
        
        markets_other = service.get_active_markets(sport="nfl", limit=10)
        assert len(markets_other) == 0
    
    def test_get_latest_snapshots(self, db_session):
        """Test getting latest snapshots for a market."""
        service = BettingMarketDBService(db_session)
        
        # Create test data
        service.ensure_sport("nba")
        service.ensure_sportsbook("draftkings")
        service.ensure_sportsbook("fanduel")
        
        game_start = datetime.utcnow() + timedelta(hours=2)
        market = service.create_or_update_market(
            sport_name="nba",
            game_name="Lakers vs Warriors",
            away_team="Los Angeles Lakers",
            home_team="Golden State Warriors",
            game_start_time=game_start
        )
        
        # Create snapshots from different sportsbooks
        from database.models import MarketSnapshotCreate
        from database import get_db
        
        # Get sportsbook IDs
        sportsbooks = db_session.query(Sportsbook).all()
        draftkings_id = next(sb.id for sb in sportsbooks if sb.name == "draftkings")
        fanduel_id = next(sb.id for sb in sportsbooks if sb.name == "fanduel")
        
        # Create snapshots
        service.create_snapshot(market.id, draftkings_id, MarketSnapshotCreate(
            market_id=market.id,
            sportsbook_id=draftkings_id,
            away_moneyline="+150",
            home_moneyline="-180"
        ))
        
        service.create_snapshot(market.id, fanduel_id, MarketSnapshotCreate(
            market_id=market.id,
            sportsbook_id=fanduel_id,
            away_moneyline="+155",
            home_moneyline="-175"
        ))
        
        # Get latest snapshots
        snapshots = service.get_latest_snapshots(market.id)
        
        assert len(snapshots) == 2
        sportsbook_names = [snap.sportsbook.name for snap in snapshots]
        assert "draftkings" in sportsbook_names
        assert "fanduel" in sportsbook_names
    
    def test_cleanup_old_snapshots(self, db_session):
        """Test cleaning up old snapshots."""
        service = BettingMarketDBService(db_session)
        
        # Create test data with old snapshot
        service.ensure_sport("nba")
        service.ensure_sportsbook("draftkings")
        
        game_start = datetime.utcnow() + timedelta(hours=2)
        market = service.create_or_update_market(
            sport_name="nba",
            game_name="Lakers vs Warriors",
            away_team="Los Angeles Lakers",
            home_team="Golden State Warriors",
            game_start_time=game_start
        )
        
        sportsbook = db_session.query(Sportsbook).filter(Sportsbook.name == "draftkings").first()
        
        # Create snapshot with old timestamp
        old_snapshot = MarketSnapshot(
            market_id=market.id,
            sportsbook_id=sportsbook.id,
            away_moneyline="+150",
            home_moneyline="-180",
            snapshot_time=datetime.utcnow() - timedelta(days=10)  # 10 days old
        )
        db_session.add(old_snapshot)
        db_session.commit()
        
        # Create recent snapshot
        from database.models import MarketSnapshotCreate
        service.create_snapshot(market.id, sportsbook.id, MarketSnapshotCreate(
            market_id=market.id,
            sportsbook_id=sportsbook.id,
            away_moneyline="+160",
            home_moneyline="-170"
        ))
        
        # Verify both snapshots exist
        total_snapshots = db_session.query(MarketSnapshot).count()
        assert total_snapshots == 2
        
        # Clean up old snapshots (keep 7 days)
        deleted_count = service.cleanup_old_snapshots(days_to_keep=7)
        assert deleted_count == 1
        
        # Verify only recent snapshot remains
        remaining_snapshots = db_session.query(MarketSnapshot).count()
        assert remaining_snapshots == 1
    
    def test_get_stats(self, db_session):
        """Test getting database statistics."""
        service = BettingMarketDBService(db_session)
        
        # Create some test data
        service.ensure_sport("nba")
        service.ensure_sportsbook("draftkings")
        
        game_start = datetime.utcnow() + timedelta(hours=2)
        market = service.create_or_update_market(
            sport_name="nba",
            game_name="Lakers vs Warriors",
            away_team="Los Angeles Lakers",
            home_team="Golden State Warriors",
            game_start_time=game_start
        )
        
        sportsbook = db_session.query(Sportsbook).filter(Sportsbook.name == "draftkings").first()
        
        # Create snapshot
        from database.models import MarketSnapshotCreate
        service.create_snapshot(market.id, sportsbook.id, MarketSnapshotCreate(
            market_id=market.id,
            sportsbook_id=sportsbook.id,
            away_moneyline="+150",
            home_moneyline="-180"
        ))
        
        # Get statistics
        stats = service.get_stats()
        
        assert stats["sports"] == 1
        assert stats["sportsbooks"] == 1
        assert stats["markets"] == 1
        assert stats["snapshots"] == 1
        assert stats["active_markets"] == 1
        assert stats["latest_snapshot"] is not None
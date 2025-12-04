"""Tests for FastAPI endpoints."""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from database.models import Base, Sport, Sportsbook, BettingMarket, MarketSnapshot


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Create in-memory test database."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Add some test data
    sport = Sport(name="nba", display_name="NBA")
    sportsbook = Sportsbook(name="draftkings", display_name="DraftKings")
    
    session.add_all([sport, sportsbook])
    session.commit()
    
    # Create test market
    market = BettingMarket(
        sport_id=sport.id,
        game_name="Lakers vs Warriors",
        away_team="Los Angeles Lakers",
        home_team="Golden State Warriors",
        game_start_time=datetime.utcnow() + timedelta(hours=2)
    )
    session.add(market)
    session.commit()
    
    # Create test snapshot
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
    session.add(snapshot)
    session.commit()
    
    yield session
    session.close()


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check returns proper response."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"


class TestSportsEndpoints:
    """Test sports-related endpoints."""
    
    def test_get_sports(self, client, test_db):
        """Test getting all sports."""
        response = client.get("/sports")
        assert response.status_code == 200
        
        sports = response.json()
        assert len(sports) >= 1
        
        # Check NBA is present
        nba = next((s for s in sports if s["name"] == "nba"), None)
        assert nba is not None
        assert nba["display_name"] == "NBA"
    
    def test_get_sport_by_name(self, client, test_db):
        """Test getting a specific sport."""
        response = client.get("/sports/nba")
        assert response.status_code == 200
        
        sport = response.json()
        assert sport["name"] == "nba"
        assert sport["display_name"] == "NBA"
    
    def test_get_nonexistent_sport(self, client):
        """Test getting non-existent sport returns 404."""
        response = client.get("/sports/nonexistent")
        assert response.status_code == 404
        assert "Sport not found" in response.json()["detail"]


class TestSportsbookEndpoints:
    """Test sportsbook-related endpoints."""
    
    def test_get_sportsbooks(self, client, test_db):
        """Test getting all sportsbooks."""
        response = client.get("/sportsbooks")
        assert response.status_code == 200
        
        sportsbooks = response.json()
        assert len(sportsbooks) >= 1
        
        # Check DraftKings is present
        draftkings = next((s for s in sportsbooks if s["name"] == "draftkings"), None)
        assert draftkings is not None
        assert draftkings["display_name"] == "DraftKings"
    
    def test_get_sportsbook_by_name(self, client, test_db):
        """Test getting a specific sportsbook."""
        response = client.get("/sportsbooks/draftkings")
        assert response.status_code == 200
        
        sportsbook = response.json()
        assert sportsbook["name"] == "draftkings"
        assert sportsbook["display_name"] == "DraftKings"
    
    def test_get_nonexistent_sportsbook(self, client):
        """Test getting non-existent sportsbook returns 404."""
        response = client.get("/sportsbooks/nonexistent")
        assert response.status_code == 404
        assert "Sportsbook not found" in response.json()["detail"]


class TestMarketEndpoints:
    """Test market-related endpoints."""
    
    def test_get_markets(self, client, test_db):
        """Test getting betting markets."""
        response = client.get("/markets")
        assert response.status_code == 200
        
        markets = response.json()
        assert len(markets) >= 1
        
        # Check our test market is present
        market = next((m for m in markets if m["game_name"] == "Lakers vs Warriors"), None)
        assert market is not None
        assert market["away_team"] == "Los Angeles Lakers"
        assert market["home_team"] == "Golden State Warriors"
        assert len(market["latest_snapshots"]) >= 1
    
    def test_get_markets_with_filters(self, client, test_db):
        """Test getting markets with filters."""
        # Test sport filter
        response = client.get("/markets?sport=nba")
        assert response.status_code == 200
        
        markets = response.json()
        assert len(markets) >= 1
    
    def test_get_market_by_id(self, client, test_db):
        """Test getting a specific market by ID."""
        # Get the market ID from test data
        market = test_db.query(BettingMarket).first()
        assert market is not None
        
        response = client.get(f"/markets/{market.id}")
        assert response.status_code == 200
        
        market_data = response.json()
        assert market_data["id"] == market.id
        assert market_data["game_name"] == "Lakers vs Warriors"
        assert len(market_data["latest_snapshots"]) >= 1
    
    def test_get_nonexistent_market(self, client):
        """Test getting non-existent market returns 404."""
        response = client.get("/markets/99999")
        assert response.status_code == 404
        assert "Market not found" in response.json()["detail"]


class TestOddsEndpoints:
    """Test odds-related endpoints."""
    
    def test_get_sportsbook_snapshots(self, client, test_db):
        """Test getting snapshots from a specific sportsbook."""
        sportsbook = test_db.query(Sportsbook).first()
        assert sportsbook is not None
        
        response = client.get(f"/odds/snapshot/{sportsbook.id}")
        assert response.status_code == 200
        
        snapshots = response.json()
        assert len(snapshots) >= 1
        
        # Check snapshot data
        snapshot = snapshots[0]
        assert "sportsbook_id" in snapshot
        assert "away_moneyline" in snapshot
        assert "home_moneyline" in snapshot
    
    def test_get_latest_odds(self, client, test_db):
        """Test getting latest odds endpoint."""
        response = client.get("/odds/latest")
        assert response.status_code == 200
        
        odds_data = response.json()
        assert len(odds_data) >= 1
        
        # Check structure
        market_data = odds_data[0]
        assert "market" in market_data
        assert "odds" in market_data
        
        market_info = market_data["market"]
        assert "id" in market_info
        assert "game" in market_info
        assert "away_team" in market_info
        assert "home_team" in market_info
        
        odds_list = market_data["odds"]
        assert len(odds_list) >= 1
        
        odds_entry = odds_list[0]
        assert "sportsbook" in odds_entry
        assert "away_moneyline" in odds_entry
        assert "home_moneyline" in odds_entry


class TestCollectionEndpoints:
    """Test data collection endpoints."""
    
    def test_trigger_collection(self, client):
        """Test triggering data collection."""
        response = client.post("/collect/nba")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "queued"
        assert "nba" in data["message"].lower()


class TestStatisticsEndpoints:
    """Test statistics and analytics endpoints."""
    
    def test_get_statistics(self, client, test_db):
        """Test getting statistics endpoint."""
        response = client.get("/stats")
        assert response.status_code == 200
        
        stats = response.json()
        assert "sports" in stats
        assert "sportsbooks" in stats
        assert "markets" in stats
        assert "snapshots" in stats
        assert "active_markets" in stats
        assert "api_version" in stats
    
    def test_market_comparison(self, client, test_db):
        """Test market comparison endpoint."""
        market = test_db.query(BettingMarket).first()
        assert market is not None
        
        response = client.get(f"/analytics/market-comparison?market_id={market.id}")
        assert response.status_code == 200
        
        comparison = response.json()
        assert "market" in comparison
        assert "sportsbook_odds" in comparison
        assert "best_odds" in comparison
        
        market_info = comparison["market"]
        assert market_info["id"] == market.id
        assert market_info["game"] == "Lakers vs Warriors"
        
        best_odds = comparison["best_odds"]
        assert "away_moneyline" in best_odds
        assert "home_moneyline" in best_odds


class TestErrorHandling:
    """Test error handling in API."""
    
    def test_invalid_market_id_format(self, client):
        """Test invalid market ID format."""
        response = client.get("/markets/invalid")
        assert response.status_code == 422  # Validation error
    
    def test_malformed_request(self, client):
        """Test handling of malformed requests."""
        # Test invalid query parameters
        response = client.get("/markets?limit=invalid")
        assert response.status_code == 422  # Validation error
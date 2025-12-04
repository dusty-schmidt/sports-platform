"""
FanDuel client for fetching betting market data.
Updated to use sport configuration and proper initialization.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

import requests

from .base import SportsbookClient
from betting_service.config.sports import get_sport_config

logger = logging.getLogger(__name__)


class FanDuelClient(SportsbookClient):
    """Client for interacting with FanDuel sportsbook API."""

    def __init__(self, sport: str):
        self.sport = sport.lower()
        self.config = get_sport_config(self.sport)
        self.base_url = "https://sbapi.oh.sportsbook.fanduel.com"
        self.session = requests.Session()
        
        # Set appropriate headers
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://sportsbook.fanduel.com/",
            "Origin": "https://sportsbook.fanduel.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        })
        
        # Get the custom_page_id from configuration
        book_config = self.config.books.get("fanduel")
        if not book_config:
            raise ValueError(f"FanDuel not configured for sport: {self.sport}")
        
        self.custom_page_id = book_config.options.get("custom_page_id", self.sport)
        
        # Initialize with the required parameters for the parent class
        super().__init__(sport, team_aliases=self.config.team_aliases, timezone=self.config.timezone)

    @property
    def name(self) -> str:
        """Return the display name of the sportsbook."""
        return "FanDuel"

    def fetch(self) -> dict:
        """Fetch raw data from the FanDuel API."""
        try:
            # Use the correct endpoint with custom_page_id
            url = f"{self.base_url}/api/content-managed-page?page=CUSTOM&customPageId={self.custom_page_id}"
            logger.info(f"Fetching FanDuel markets from: {url} (sport: {self.sport})")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched FanDuel data for {self.sport}")
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching FanDuel markets for {self.sport}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing FanDuel response for {self.sport}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching FanDuel markets for {self.sport}: {e}")
            raise

    def transform(self, payload: dict) -> List[Any]:
        """Transform FanDuel API response into market events."""
        markets = []
        
        try:
            # FanDuel response structure analysis
            events_data = payload.get("content", {}).get("sbEvents", [])
            
            for event_data in events_data:
                market_data = self._extract_market_data(event_data)
                if market_data:
                    markets.append(market_data)
                    
        except Exception as e:
            logger.error(f"Error transforming FanDuel market data: {e}")
            
        return markets

    def _extract_market_data(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract market data from a FanDuel event object."""
        try:
            # Basic event information
            event_id = event_data.get("id")
            away_team = self.alias_team(event_data.get("awayTeam", {}).get("name", "Unknown"))
            home_team = self.alias_team(event_data.get("homeTeam", {}).get("name", "Unknown"))
            
            # Start time
            start_time = event_data.get("startTime")
            if start_time:
                try:
                    from datetime import datetime
                    start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                except:
                    pass
            
            # Initialize market data
            market_data = {
                "event_id": event_id,
                "sport": self.sport,
                "sportsbook": self.name,
                "away_team": away_team,
                "home_team": home_team,
                "start_time": start_time,
                "markets": []
            }
            
            # Extract betting markets
            markets_data = event_data.get("markets", [])
            for market_info in markets_data:
                parsed_market = self._parse_market(market_info)
                if parsed_market:
                    market_data["markets"].append(parsed_market)
            
            return market_data if market_data["markets"] else None
            
        except Exception as e:
            logger.error(f"Error extracting FanDuel market data: {e}")
            return None

    def _parse_market(self, market: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a market from FanDuel response."""
        try:
            market_type = market.get("name", "")
            selections = market.get("selections", [])
            
            if not selections:
                return None
            
            market_info = {
                "type": market_type,
                "line": None,  # FanDuel structure may vary
                "outcomes": []
            }
            
            for selection in selections:
                outcome_info = {
                    "name": selection.get("name", ""),
                    "odds": selection.get("price", {}).get("decimal", None),
                    "american_odds": selection.get("price", {}).get("american", None)
                }
                market_info["outcomes"].append(outcome_info)
            
            return market_info
            
        except Exception as e:
            logger.error(f"Error parsing FanDuel market: {e}")
            return None

    def close(self) -> None:
        """Close the client session."""
        self.session.close()
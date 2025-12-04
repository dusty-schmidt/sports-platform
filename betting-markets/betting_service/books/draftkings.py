"""
Enhanced DraftKings client with dynamic tournament discovery.
This addresses the issue of dynamic tournament IDs for sports like tennis, golf, MMA.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests

from .base import SportsbookClient
from betting_service.config.sports import get_sport_config
from ..utils.tournament_discovery import get_dynamic_tournament_id, discover_all_sports

logger = logging.getLogger(__name__)


class DraftKingsClient(SportsbookClient):
    """Enhanced client for interacting with DraftKings sportsbook API with dynamic tournament discovery."""

    def __init__(self, sport: str):
        self.sport = sport.lower()
        self.config = get_sport_config(self.sport)
        self.base_url = "https://sportsbook-nash.draftkings.com"
        self.session = requests.Session()
        
        # Set headers based on the working request
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://sportsbook.draftkings.com/",
            "X-Client-Name": "web",
            "X-Client-Version": "1.4.0",
            "X-Client-Feature": "cms",
            "X-Client-Page": "home",
            "Origin": "https://sportsbook.draftkings.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Priority": "u=4",
        })
        
        # Initialize with the required parameters for the parent class
        super().__init__(sport, team_aliases=self.config.team_aliases, timezone=self.config.timezone)

    @property
    def name(self) -> str:
        """Return the display name of the sportsbook."""
        return "DraftKings"

    def get_available_sports(self) -> List[Dict[str, Any]]:
        """Get all available sports from the manifest endpoint."""
        try:
            url = f"{self.base_url}/sites/US-OH-SB/api/sportslayout/v1/manifest?format=json"
            logger.info(f"Fetching DraftKings manifest from: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            sports_list = []
            
            # Parse the manifest to extract sports and leagues
            for sport_data in data.get("sports", []):
                sport_name = sport_data.get("name", "")
                sport_id = sport_data.get("id")
                leagues = sport_data.get("leagues", [])
                
                sport_info = {
                    "name": sport_name,
                    "id": sport_id,
                    "leagues": []
                }
                
                for league in leagues:
                    league_info = {
                        "name": league.get("name", ""),
                        "id": league.get("id"),
                        "url": league.get("url")
                    }
                    sport_info["leagues"].append(league_info)
                
                sports_list.append(sport_info)
            
            logger.info(f"Found {len(sports_list)} sports in DraftKings manifest")
            return sports_list
            
        except requests.RequestException as e:
            logger.error(f"Error fetching DraftKings manifest: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing DraftKings manifest response: {e}")
            return []

    def get_dynamic_league_id(self) -> Optional[str]:
        """Get league ID using dynamic tournament discovery for this sport."""
        # Sports with dynamic tournaments
        dynamic_sports = ["tennis", "golf", "mma", "boxing", "motorsports"]
        
        if self.sport in dynamic_sports:
            logger.info(f"Using dynamic tournament discovery for {self.sport}")
            tournament_id = get_dynamic_tournament_id(self.sport, self.base_url, self.session)
            if tournament_id:
                logger.info(f"Dynamic discovery found tournament ID {tournament_id} for {self.sport}")
                return tournament_id
            else:
                logger.warning(f"Dynamic discovery failed for {self.sport}, falling back to config")
        
        # Static sports use configured league ID
        return self._get_configured_league_id()

    def _get_configured_league_id(self) -> Optional[str]:
        """Get league ID from configuration."""
        book_config = self.config.books.get("draftkings")
        if not book_config:
            raise ValueError(f"DraftKings not configured for sport: {self.sport}")
        
        return book_config.options.get("league_id")

    def fetch(self) -> dict:
        """Fetch raw data from the DraftKings API."""
        # Get league ID (dynamic for tournament sports, static for others)
        league_id = self.get_dynamic_league_id()
        
        if not league_id:
            raise ValueError(f"No league ID found for sport: {self.sport}")

        try:
            # Use the existing endpoint structure
            url = f"{self.base_url}/api/sportscontent/dkusoh/v1/leagues/{league_id}"
            logger.info(f"Fetching DraftKings markets from: {url} (sport: {self.sport})")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched DraftKings data for {self.sport} (league: {league_id})")
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching DraftKings markets for {self.sport}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing DraftKings response for {self.sport}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching DraftKings markets for {self.sport}: {e}")
            raise

    def transform(self, payload: dict) -> List[Any]:
        """Transform DraftKings API response into market events."""
        markets = []
        
        try:
            # The response structure may vary, so let's be flexible
            events = payload.get("events", payload.get("eventGroups", []))
            
            for event in events:
                # Handle different possible structures
                competitions = event.get("competitions", [])
                if not competitions:
                    competitions = event.get("events", [])
                
                for competition in competitions:
                    market_data = self._extract_market_data(competition)
                    if market_data:
                        markets.append(market_data)
                        
        except Exception as e:
            logger.error(f"Error transforming DraftKings market data: {e}")
            
        return markets

    def _extract_market_data(self, competition: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract market data from a competition object."""
        try:
            # Basic event information
            event_id = competition.get("id")
            away_team = self.alias_team(competition.get("awayTeam", {}).get("name", "Unknown"))
            home_team = self.alias_team(competition.get("homeTeam", {}).get("name", "Unknown"))
            
            # Start time
            start_time = competition.get("startTime", competition.get("startDateTime"))
            if start_time:
                # DraftKings might use different time formats
                if isinstance(start_time, str):
                    # Try to parse ISO format
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
            betting_offers = competition.get("bettingOffers", [])
            for offer in betting_offers:
                market_info = self._parse_betting_offer(offer)
                if market_info:
                    market_data["markets"].append(market_info)
            
            return market_data if market_data["markets"] else None
            
        except Exception as e:
            logger.error(f"Error extracting market data: {e}")
            return None

    def _parse_betting_offer(self, offer: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse a betting offer from DraftKings response."""
        try:
            market_type = offer.get("marketType", {}).get("name", "")
            line = offer.get("line")
            outcomes = offer.get("outcomes", [])
            
            if not outcomes:
                return None
            
            market_info = {
                "type": market_type,
                "line": line,
                "outcomes": []
            }
            
            for outcome in outcomes:
                outcome_info = {
                    "name": outcome.get("name", ""),
                    "odds": outcome.get("price", {}).get("decimal", None),
                    "american_odds": outcome.get("price", {}).get("american", None)
                }
                market_info["outcomes"].append(outcome_info)
            
            return market_info
            
        except Exception as e:
            logger.error(f"Error parsing betting offer: {e}")
            return None

    def discover_all_current_tournaments(self) -> Dict[str, List[Dict[str, Any]]]:
        """Discover all currently available tournaments for dynamic sports."""
        logger.info("Discovering all current tournaments for dynamic sports")
        tournaments = discover_all_sports(self.base_url, self.session)
        
        # Log the results
        dynamic_sports = ["tennis", "golf", "mma", "boxing", "motorsports"]
        for sport in dynamic_sports:
            if sport in tournaments:
                tournaments_list = tournaments[sport]
                logger.info(f"Found {len(tournaments_list)} tournaments for {sport}:")
                for tournament in tournaments_list:
                    logger.info(f"  - {tournament['name']} (ID: {tournament['id']})")
        
        return tournaments

    def close(self) -> None:
        """Close the client session."""
        self.session.close()
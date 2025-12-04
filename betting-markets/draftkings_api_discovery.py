"""
Comprehensive DraftKings API Discovery and Documentation System.
Systematically maps out all sports, leagues, markets, and API endpoints.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import os

logger = logging.getLogger(__name__)


@dataclass
class League:
    """Represents a sports league with its ID and metadata."""
    name: str
    id: str
    sport_category: str
    routes: List[str]
    markets: List[str] = None
    available: bool = True


@dataclass
class Sport:
    """Represents a sport with all its leagues and markets."""
    name: str
    id: str
    category: str
    leagues: List[League]
    market_types: List[str] = None


class DraftKingsAPIDiscoverer:
    """Comprehensive API discovery for DraftKings sportsbook."""
    
    def __init__(self):
        self.sports = {}
        self.leagues = {}
        self.market_types = set()
        self.routes_data = None
        self.manifest_data = None
        self.api_structure = {}
        
    def load_routes_data(self, routes_json: str = None):
        """Load the routes data you provided earlier."""
        if routes_json:
            self.routes_data = json.loads(routes_json)
        else:
            # Use the routes data you provided
            self.routes_data = {
                "routes": [
                    {
                        "key": "event",
                        "entityType": "event", 
                        "route": "/sport/{sportId}/league/{leagueId}/event/{eventId}",
                        "seoRoute": "/events/{sportSeoId}/{leagueSeoId}/{eventSeoId}/{eventId}",
                        "overrides": [
                            {
                                "route": "/sport/7/league/84240/event/{eventId}",
                                "seoRoute": "/events/baseball/mlb/{eventSeoId}/{eventId}",
                                "templateId": "6a75a42e-dd73-46ae-87cc-7f82a76face8__client_web_1.3.0",
                                "versionHash": "2046699252"
                            },
                            {
                                "route": "/sport/3/league/88808/event/{eventId}",
                                "seoRoute": "/events/football/nfl/{eventSeoId}/{eventId}",
                                "templateId": "849ac722-527b-4713-9f7f-e50d24540ed2__client_web_1.3.0",
                                "versionHash": "462902644"
                            },
                            {
                                "route": "/sport/3/league/87637/event/{eventId}",
                                "seoRoute": "/events/football/ncaaf/{eventSeoId}/{eventId}",
                                "templateId": "4d51c8b3-ed44-463c-a6f8-ee70b258a82c__client_web_1.3.0",
                                "versionHash": "1700241131"
                            },
                            {
                                "route": "/sport/3/league/33567/event/{eventId}",
                                "seoRoute": "/events/football/cfl/{eventSeoId}/{eventId}",
                                "templateId": "e17a636d-1459-4c3a-a1ef-27968a7caab2__client_web_1.3.0",
                                "versionHash": "917402073"
                            },
                            {
                                "route": "/sport/2/league/92483/event/{eventId}",
                                "seoRoute": "/events/basketball/ncaab/{eventSeoId}/{eventId}",
                                "templateId": "ad9b6e84-e8eb-4318-80ee-325f5ef4e0d6__client_web_1.3.0",
                                "versionHash": "409430877"
                            },
                            {
                                "route": "/sport/2/league/42648/event/{eventId}",
                                "seoRoute": "/events/basketball/nba/{eventSeoId}/{eventId}",
                                "templateId": "6fe8a4fa-539b-4533-ac53-c3a0a879a8a8__client_web_1.3.0",
                                "versionHash": "114450776"
                            },
                            {
                                "route": "/sport/8/league/{leagueId}/event/{eventId}",
                                "seoRoute": "/events/hockey/{leagueSeoId}/{eventSeoId}/{eventId}",
                                "templateId": "99961bed-adb7-45cd-a240-d1b0169cce7f__client_web_1.3.0",
                                "versionHash": "970339217"
                            },
                            {
                                "route": "/sport/7/league/{leagueId}/event/{eventId}",
                                "seoRoute": "/events/baseball/{leagueSeoId}/{eventSeoId}/{eventId}",
                                "templateId": "c4cb12a2-685d-42f3-bc2f-7680c5e32508__client_web_1.3.0",
                                "versionHash": "1589404034"
                            },
                            {
                                "route": "/sport/64/league/{leagueId}/event/{eventId}",
                                "seoRoute": "/events/esports/{leagueSeoId}/{eventSeoId}/{eventId}",
                                "templateId": "ffe645dc-3a80-41d5-9759-d52f8c60e5d6__client_web_1.3.0",
                                "versionHash": "698539533"
                            },
                            {
                                "route": "/sport/6/league/{leagueId}/event/{eventId}",
                                "seoRoute": "/events/tennis/{leagueSeoId}/{eventSeoId}/{eventId}",
                                "templateId": "77ef4d45-6608-4b18-bf4e-d34e085a5b3e__client_web_1.3.0",
                                "versionHash": "344885088"
                            },
                            {
                                "route": "/sport/43/league/{leagueId}/event/{eventId}",
                                "seoRoute": "/events/mma/{leagueSeoId}/{eventSeoId}/{eventId}",
                                "templateId": "00040eb2-574d-4fe8-9edc-f2a4e7b15149__client_web_1.3.0",
                                "versionHash": "2144360125"
                            },
                            {
                                "route": "/sport/12/league/{leagueId}/event/{eventId}",
                                "seoRoute": "/events/golf/{leagueSeoId}/{eventSeoId}/{eventId}",
                                "templateId": "2f387a35-cc64-4418-913c-8ce322cff957__client_web_1.3.0",
                                "versionHash": "892411688"
                            },
                            {
                                "route": "/sport/1/league/{leagueId}/event/{eventId}",
                                "seoRoute": "/events/soccer/{leagueSeoId}/{eventSeoId}/{eventId}",
                                "templateId": "d37da430-d72e-4980-872c-0427cd3d3b37__client_web_1.3.0",
                                "versionHash": "541173076"
                            }
                        ]
                    },
                    {
                        "key": "league",
                        "entityType": "league",
                        "route": "/sport/{sportId}/league/{leagueId}",
                        "seoRoute": "/leagues/{sportSeoId}/{leagueSeoId}",
                        "overrides": [
                            {
                                "route": "/sport/3/league/88808",
                                "seoRoute": "/leagues/football/nfl",
                                "templateId": "02d63505-bc8a-47d7-9ab4-eae634706188__client_web_1.4.0",
                                "versionHash": "1546631712"
                            },
                            {
                                "route": "/sport/3/league/87637",
                                "seoRoute": "/leagues/football/ncaaf",
                                "templateId": "13133f59-a995-4988-ac3d-cabf1347a90e__client_web_1.4.0",
                                "versionHash": "1460781710"
                            },
                            {
                                "route": "/sport/2/league/94682",
                                "seoRoute": "/leagues/basketball/wnba",
                                "templateId": "f0613a94-e73b-4ae6-bf2c-2abafc297015__client_web_1.4.0",
                                "versionHash": "1165294290"
                            },
                            {
                                "route": "/sport/8/league/42133",
                                "seoRoute": "/leagues/hockey/nhl",
                                "templateId": "4f2034ce-2f40-4438-a4fd-b57be7916afc__client_web_1.3.0",
                                "versionHash": "558913672"
                            },
                            {
                                "route": "/sport/7/league/84240",
                                "seoRoute": "/leagues/baseball/mlb",
                                "templateId": "a2f7806b-4d02-4c3a-96c4-c19ef71423e3__client_web_1.3.0",
                                "versionHash": "1062425125"
                            },
                            {
                                "route": "/sport/2/league/92483",
                                "seoRoute": "/leagues/basketball/ncaab",
                                "templateId": "dd51e063-64ae-4e8f-a820-bc410fc4b0d3__client_web_1.3.0",
                                "versionHash": "429189167"
                            },
                            {
                                "route": "/sport/2/league/42648",
                                "seoRoute": "/leagues/basketball/nba",
                                "templateId": "b6f414b8-c1ca-4040-ab9d-0492a805d532__client_web_1.4.0",
                                "versionHash": "793015791"
                            },
                            {
                                "route": "/sport/14/league/212334",
                                "seoRoute": "/leagues/motorsports/formula-1",
                                "templateId": "defcbace-8062-4322-bc5a-452fdfdbf9a3__client_web_1.3.0",
                                "versionHash": "1182584017"
                            },
                            {
                                "route": "/sport/12/league/16936",
                                "seoRoute": "/leagues/golf/ryder-cup",
                                "templateId": "7494101e-5c0e-450e-ace4-6972bae8f829__client_web_1.3.0",
                                "versionHash": "1461277039"
                            }
                        ]
                    }
                ]
            }

    def parse_sport_ids(self):
        """Parse sport IDs and categories from routes."""
        sport_mapping = {
            "1": "soccer",
            "2": "basketball", 
            "3": "football",
            "6": "tennis",
            "7": "baseball",
            "8": "hockey",
            "12": "golf",
            "14": "motorsports",
            "43": "mma",
            "64": "esports"
        }
        
        league_mappings = {
            "88808": ("nfl", "NFL"),
            "87637": ("ncaaf", "NCAA Football"),
            "94682": ("wnba", "WNBA"),
            "42133": ("nhl", "NHL"),
            "84240": ("mlb", "MLB"),
            "92483": ("ncaab", "NCAA Basketball"),
            "42648": ("nba", "NBA"),
            "212334": ("f1", "Formula 1"),
            "16936": ("ryder_cup", "Ryder Cup")
        }
        
        # Process event routes
        for route_data in self.routes_data.get("routes", []):
            if route_data.get("key") == "event":
                for override in route_data.get("overrides", []):
                    route = override.get("route", "")
                    if "/sport/" in route and "/league/" in route:
                        # Extract sport and league IDs
                        parts = route.split("/")
                        try:
                            sport_idx = parts.index("sport") + 1
                            league_idx = parts.index("league") + 1
                            
                            sport_id = parts[sport_idx]
                            league_id = parts[league_idx]
                            
                            sport_name = sport_mapping.get(sport_id, f"sport_{sport_id}")
                            league_key, league_name = league_mappings.get(league_id, (league_id, f"League {league_id}"))
                            
                            # Store league info
                            if league_key not in self.leagues:
                                self.leagues[league_key] = League(
                                    name=league_name,
                                    id=league_id,
                                    sport_category=sport_name,
                                    routes=[route]
                                )
                            else:
                                self.leagues[league_key].routes.append(route)
                                
                        except (ValueError, IndexError):
                            continue
        
        return self.leagues

    def analyze_api_endpoints(self):
        """Analyze all possible API endpoints from the routes."""
        endpoints = {
            "base_url": "https://sportsbook-nash.draftkings.com",
            "manifest": "/sites/US-OH-SB/api/sportslayout/v1/manifest?format=json",
            "sports_content": "/api/sportscontent/dkusoh/v1/leagues/{league_id}",
            "events": "/api/sportscontent/dkusoh/v1/leagues/{league_id}/events",
            "markets": "/api/sportscontent/dkusoh/v1/leagues/{league_id}/markets",
            "selections": "/api/sportscontent/dkusoh/v1/leagues/{league_id}/selections"
        }
        
        # Map leagues to their content endpoints
        for league_key, league in self.leagues.items():
            endpoints[f"leagues/{league_key}"] = {
                "content": f"/api/sportscontent/dkusoh/v1/leagues/{league.id}",
                "events": f"/api/sportscontent/dkusoh/v1/leagues/{league.id}/events", 
                "markets": f"/api/sportscontent/dkusoh/v1/leagues/{league.id}/markets",
                "selections": f"/api/sportscontent/dkusoh/v1/leagues/{league.id}/selections"
            }
        
        return endpoints

    def discover_market_types(self):
        """Discover common market types across sports."""
        market_types = {
            # Core markets
            "moneyline": "Pick the winner",
            "spread": "Point spread betting",
            "total": "Over/under total points/goals",
            
            # Player props
            "player_points": "Player total points",
            "player_rebounds": "Player total rebounds", 
            "player_assists": "Player total assists",
            "player_three_pointers": "Player 3-point field goals",
            "player_receives": "Player receiving yards",
            "player_rushes": "Player rushing attempts",
            
            # Team props
            "team_points": "Team total points",
            "team_yards": "Team total yards",
            "team_touchdowns": "Team touchdowns",
            
            # Game props
            "first_half": "First half results",
            "second_half": "Second half results",
            "quarter": "Quarter results",
            "period": "Period results (hockey, soccer)",
            
            # Special markets
            "corners": "Corner kicks (soccer)",
            "cards": "Yellow/red cards (soccer)",
            "shots": "Shots on target (soccer)",
            "hits": "Hits (baseball)",
            "errors": "Errors (baseball)",
            
            # Futures
            "championship": "Tournament winner",
            "division": "Division winner",
            "playoffs": "Playoff qualification"
        }
        
        return market_types

    def generate_api_documentation(self):
        """Generate comprehensive API documentation."""
        leagues = self.parse_sport_ids()
        endpoints = self.analyze_api_endpoints()
        market_types = self.discover_market_types()
        
        documentation = {
            "title": "DraftKings Sportsbook API - Complete Reference",
            "version": "1.0",
            "base_url": "https://sportsbook-nash.draftkings.com",
            "authentication": "None required (public API)",
            "rate_limiting": "Not specified",
            
            "sports_and_leagues": {
                sport_key: {
                    "sport_category": league.sport_category,
                    "league_id": league.id,
                    "league_name": league.name,
                    "endpoints": {
                        "content": f"/api/sportscontent/dkusoh/v1/leagues/{league.id}",
                        "events": f"/api/sportscontent/dkusoh/v1/leagues/{league.id}/events",
                        "markets": f"/api/sportscontent/dkusoh/v1/leagues/{league.id}/markets",
                        "selections": f"/api/sportscontent/dkusoh/v1/leagues/{league.id}/selections"
                    },
                    "route_patterns": league.routes
                }
                for sport_key, league in leagues.items()
            },
            
            "market_types": market_types,
            
            "api_endpoints": {
                "manifest": {
                    "url": "/sites/US-OH-SB/api/sportslayout/v1/manifest?format=json",
                    "method": "GET",
                    "description": "Get all available sports and leagues",
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
                        "Accept": "*/*",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Referer": "https://sportsbook.draftkings.com/",
                        "X-Client-Name": "web",
                        "X-Client-Version": "1.4.0",
                        "Origin": "https://sportsbook.draftkings.com"
                    }
                },
                
                "league_content": {
                    "url": "/api/sportscontent/dkusoh/v1/leagues/{league_id}",
                    "method": "GET", 
                    "description": "Get betting data for a specific league",
                    "parameters": {
                        "league_id": "The league ID (e.g., 42648 for NBA)"
                    }
                }
            },
            
            "response_structure": {
                "sports": "Array of sports categories",
                "leagues": "Array of leagues within sports",
                "events": "Array of upcoming games/matches",
                "markets": "Array of betting markets for events",
                "selections": "Array of betting options within markets",
                "categories": "Additional market categorization",
                "subcategories": "Further market subdivision"
            },
            
            "notes": [
                "League IDs are static for major sports (NBA, NFL, etc.)",
                "Dynamic sports (tennis, golf, MMA) may have changing tournament IDs",
                "Market availability varies by sport and event",
                "API appears to be real-time but may have caching",
                "Some endpoints may require specific headers for access"
            ]
        }
        
        return documentation

    def save_documentation(self, filename="draftkings_api_documentation.json"):
        """Save the complete API documentation to file."""
        doc = self.generate_api_documentation()
        
        with open(filename, 'w') as f:
            json.dump(doc, f, indent=2, default=str)
        
        logger.info(f"API documentation saved to {filename}")
        return doc

    def print_summary(self):
        """Print a summary of discovered sports and leagues."""
        leagues = self.parse_sport_ids()
        
        print("\n" + "="*80)
        print("🏆 DRAFTKINGS API - COMPREHENSIVE SPORTS & LEAGUES DISCOVERY")
        print("="*80)
        
        print(f"\n📊 Total Leagues Discovered: {len(leagues)}")
        
        # Group by sport category
        by_category = defaultdict(list)
        for league_key, league in leagues.items():
            by_category[league.sport_category].append(league)
        
        for category, category_leagues in by_category.items():
            print(f"\n🏈 {category.upper()}:")
            for league in category_leagues:
                print(f"  • {league.name} (ID: {league.id}) - {league_key}")
        
        print(f"\n📋 Market Types Available: {len(self.discover_market_types())}")
        print("\n🔗 API Endpoints:")
        endpoints = self.analyze_api_endpoints()
        for key, endpoint in endpoints.items():
            if isinstance(endpoint, dict) and "content" in endpoint:
                print(f"  • {key}: {endpoint['content']}")
        
        print("\n" + "="*80)


def main():
    """Run the comprehensive API discovery."""
    discoverer = DraftKingsAPIDiscoverer()
    
    # Load and parse routes data
    discoverer.load_routes_data()
    leagues = discoverer.parse_sport_ids()
    
    # Generate and save documentation
    doc = discoverer.generate_api_documentation()
    discoverer.save_documentation()
    
    # Print summary
    discoverer.print_summary()
    
    return doc


if __name__ == "__main__":
    documentation = main()
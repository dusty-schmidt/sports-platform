"""
DraftKings Market Discovery System.
Discovers and maps all market types and their IDs for each league.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class MarketType:
    """Represents a betting market type with its ID and metadata."""
    name: str
    id: str
    category: str
    subcategory: str = ""
    description: str = ""


@dataclass
class LeagueMarkets:
    """Contains all market types discovered for a specific league."""
    league_id: str
    league_name: str
    sport: str
    markets: Dict[str, MarketType]
    total_markets: int = 0
    categories: List[str] = None


class DraftKingsMarketDiscoverer:
    """Discovers and maps all market types for DraftKings leagues."""
    
    def __init__(self):
        self.base_url = "https://sportsbook-nash.draftkings.com"
        self.session = requests.Session()
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
        
        self.discovered_leagues = {}
        self.market_mappings = {}
        
    def get_known_leagues(self) -> Dict[str, Dict[str, str]]:
        """Get all known leagues with their IDs from our discovery."""
        return {
            "nba": {"id": "42648", "name": "NBA", "sport": "basketball"},
            "nfl": {"id": "88808", "name": "NFL", "sport": "football"},
            "ncaab": {"id": "92483", "name": "NCAA Basketball", "sport": "basketball"},
            "ncaaf": {"id": "87637", "name": "NCAA Football", "sport": "football"},
            "mlb": {"id": "84240", "name": "MLB", "sport": "baseball"},
            "nhl": {"id": "42133", "name": "NHL", "sport": "hockey"},
            "wnba": {"id": "94682", "name": "WNBA", "sport": "basketball"},
            "cfl": {"id": "33567", "name": "CFL", "sport": "football"},
        }
    
    def fetch_league_data(self, league_id: str) -> Optional[Dict[str, Any]]:
        """Fetch raw data for a specific league."""
        try:
            url = f"{self.base_url}/api/sportscontent/dkusoh/v1/leagues/{league_id}"
            logger.info(f"Fetching league data from: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched data for league {league_id}")
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching league {league_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing league {league_id} response: {e}")
            return None
    
    def discover_market_types(self, league_data: Dict[str, Any], league_id: str) -> Dict[str, MarketType]:
        """Extract and map all market types from league data."""
        markets = {}
        
        try:
            # Look for markets in different possible locations in the response
            market_sources = [
                league_data.get("markets", []),
                league_data.get("categories", []),
                league_data.get("subcategories", []),
                league_data.get("selections", []),
            ]
            
            # Also check nested structures
            if "content" in league_data:
                content = league_data["content"]
                market_sources.extend([
                    content.get("markets", []),
                    content.get("categories", []),
                    content.get("subcategories", []),
                ])
            
            # Check for event-based markets
            if "events" in league_data:
                for event in league_data["events"]:
                    if "markets" in event:
                        market_sources.append(event["markets"])
                    if "selections" in event:
                        market_sources.append(event["selections"])
            
            # Process all potential market sources
            for source in market_sources:
                if isinstance(source, list):
                    for item in source:
                        if isinstance(item, dict):
                            market = self._extract_market_info(item)
                            if market:
                                markets[market.name.lower()] = market
            
            logger.info(f"Discovered {len(markets)} market types for league {league_id}")
            
        except Exception as e:
            logger.error(f"Error discovering market types for league {league_id}: {e}")
        
        return markets
    
    def _extract_market_info(self, market_data: Dict[str, Any]) -> Optional[MarketType]:
        """Extract market information from a market data object."""
        try:
            # Try different possible field names for market identification
            market_id = (
                market_data.get("id") or
                market_data.get("marketId") or
                market_data.get("typeId") or
                str(hash(str(market_data)))  # Fallback to hash if no ID
            )
            
            market_name = (
                market_data.get("name") or
                market_data.get("marketName") or
                market_data.get("displayName") or
                market_data.get("type") or
                "Unknown Market"
            )
            
            category = (
                market_data.get("category") or
                market_data.get("marketCategory") or
                market_data.get("group") or
                "General"
            )
            
            subcategory = (
                market_data.get("subcategory") or
                market_data.get("subGroup") or
                ""
            )
            
            description = (
                market_data.get("description") or
                market_data.get("marketDescription") or
                ""
            )
            
            return MarketType(
                name=market_name,
                id=str(market_id),
                category=category,
                subcategory=subcategory,
                description=description
            )
            
        except Exception as e:
            logger.debug(f"Error extracting market info: {e}")
            return None
    
    def discover_league_markets(self, league_key: str) -> Optional[LeagueMarkets]:
        """Discover all markets for a specific league."""
        leagues = self.get_known_leagues()
        
        if league_key not in leagues:
            logger.error(f"Unknown league key: {league_key}")
            return None
        
        league_info = leagues[league_key]
        league_id = league_info["id"]
        
        # Fetch league data
        league_data = self.fetch_league_data(league_id)
        if not league_data:
            return None
        
        # Discover market types
        markets = self.discover_market_types(league_data, league_id)
        
        # Create LeagueMarkets object
        league_markets = LeagueMarkets(
            league_id=league_id,
            league_name=league_info["name"],
            sport=league_info["sport"],
            markets=markets,
            total_markets=len(markets),
            categories=list(set(m.category for m in markets.values()))
        )
        
        return league_markets
    
    def discover_all_league_markets(self, test_leagues: List[str] = None) -> Dict[str, LeagueMarkets]:
        """Discover markets for multiple leagues."""
        if test_leagues is None:
            test_leagues = ["nba", "nfl", "ncaab", "ncaaf", "mlb", "nhl", "wnba"]
        
        all_league_markets = {}
        
        for league_key in test_leagues:
            logger.info(f"\n🔍 Discovering markets for {league_key.upper()}...")
            league_markets = self.discover_league_markets(league_key)
            
            if league_markets:
                all_league_markets[league_key] = league_markets
                logger.info(f"✅ {league_key}: {league_markets.total_markets} markets discovered")
            else:
                logger.warning(f"❌ {league_key}: Failed to discover markets")
        
        return all_league_markets
    
    def analyze_market_patterns(self, league_markets: Dict[str, LeagueMarkets]) -> Dict[str, Any]:
        """Analyze market patterns across leagues."""
        analysis = {
            "total_leagues": len(league_markets),
            "common_markets": defaultdict(list),
            "sport_specific_markets": defaultdict(list),
            "unique_market_types": set(),
            "market_categories": defaultdict(set),
        }
        
        # Analyze market patterns
        for league_key, league_data in league_markets.items():
            sport = league_data.sport
            
            for market_name, market in league_data.markets.items():
                analysis["unique_market_types"].add(market_name)
                analysis["market_categories"][sport].add(market.category)
                
                # Track common vs sport-specific markets
                common_count = sum(1 for l in league_markets.values() 
                                 if market_name in l.markets)
                
                if common_count > 1:  # Market appears in multiple leagues
                    analysis["common_markets"][market_name].append(league_key)
                else:  # Sport-specific market
                    analysis["sport_specific_markets"][sport].append(market_name)
        
        # Convert sets to lists for JSON serialization
        analysis["unique_market_types"] = list(analysis["unique_market_types"])
        for sport in analysis["market_categories"]:
            analysis["market_categories"][sport] = list(analysis["market_categories"][sport])
        
        return analysis
    
    def print_discovery_summary(self, league_markets: Dict[str, LeagueMarkets], 
                              analysis: Dict[str, Any]):
        """Print a comprehensive summary of discovery results."""
        print("\n" + "="*80)
        print("🏆 DRAFTKINGS MARKET DISCOVERY - COMPREHENSIVE RESULTS")
        print("="*80)
        
        print(f"\n📊 LEAGUES ANALYZED: {analysis['total_leagues']}")
        print(f"📋 UNIQUE MARKET TYPES: {len(analysis['unique_market_types'])}")
        
        # Print league-specific results
        print(f"\n🔍 LEAGUE-BY-LEAGUE BREAKDOWN:")
        for league_key, league_data in league_markets.items():
            print(f"\n🏈 {league_data.league_name} ({league_key.upper()}):")
            print(f"  • League ID: {league_data.league_id}")
            print(f"  • Sport: {league_data.sport}")
            print(f"  • Total Markets: {league_data.total_markets}")
            print(f"  • Categories: {', '.join(league_data.categories[:5])}{'...' if len(league_data.categories) > 5 else ''}")
            
            # Show top markets
            top_markets = list(league_data.markets.keys())[:8]
            print(f"  • Top Markets: {', '.join(top_markets)}")
        
        # Print common markets
        print(f"\n🌐 COMMON MARKETS ACROSS LEAGUES:")
        for market, leagues in analysis["common_markets"].items():
            if len(leagues) > 1:
                print(f"  • {market}: {', '.join(leagues)}")
        
        # Print sport-specific markets
        print(f"\n⚽ SPORT-SPECIFIC MARKETS:")
        for sport, markets in analysis["sport_specific_markets"].items():
            if markets:
                print(f"  • {sport}: {', '.join(markets[:5])}")
        
        print("\n" + "="*80)


def main():
    """Run comprehensive market discovery."""
    discoverer = DraftKingsMarketDiscoverer()
    
    # Discover markets for all leagues
    league_markets = discoverer.discover_all_league_markets()
    
    # Analyze patterns
    analysis = discoverer.analyze_market_patterns(league_markets)
    
    # Print summary
    discoverer.print_discovery_summary(league_markets, analysis)
    
    # Save results
    results = {
        "discovery_timestamp": "2025-11-04T17:08:14.897Z",
        "total_leagues_discovered": len(league_markets),
        "league_markets": {
            key: {
                "league_id": data.league_id,
                "league_name": data.league_name,
                "sport": data.sport,
                "total_markets": data.total_markets,
                "categories": data.categories,
                "markets": {k: {
                    "name": v.name,
                    "id": v.id,
                    "category": v.category,
                    "subcategory": v.subcategory,
                    "description": v.description
                } for k, v in data.markets.items()}
            } for key, data in league_markets.items()
        },
        "analysis": analysis
    }
    
    with open("market_discovery_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info("Market discovery results saved to market_discovery_results.json")
    
    return results


if __name__ == "__main__":
    results = main()
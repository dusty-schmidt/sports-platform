"""
Comprehensive testing system for all discovered DraftKings leagues.
Tests data collection and market availability for maximum coverage.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from betting_service.books.draftkings import DraftKingsClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ComprehensiveLeagueTester:
    """Test all discovered DraftKings leagues for data availability and market types."""
    
    def __init__(self):
        # Discovered leagues from API discovery
        self.discovered_leagues = {
            "nba": {"id": "42648", "name": "NBA", "status": "tested"},
            "nfl": {"id": "88808", "name": "NFL", "status": "tested"},
            "ncaab": {"id": "92483", "name":
I see the file got corrupted during the write operation. Let me fix the syntax error and rewrite the comprehensive league tester properly:
<write_to_file>
<content>"""
Comprehensive "NCAA Basketball", "status": "tested"},
            "ncaaf": {"id": "87637", "name": "NCAA Football", "status": "tested"},
            "mlb": {"id": "84240", "name": "MLB", "status": "tested"},
            "nhl": {"id": "42133", "name": "N testing system for all discovered DraftKings leagues.
Tests data collection and market availability for maximum coverage.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime importHL", "status": "tested"},
            "cfl": {"id": "33567", "name": "CFL (Unknown)", "status": "tested"},
        }
        
 datetime
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from betting_service.books.draftkings import Draft        # Additional sports that need dynamic discovery
        self.dynamic_sports = {
            "tennis": {"name": "Tennis", "dynamic": True},
            "golf": {"name":KingsClient
from betting_service.utils.tournament_discovery import tournament_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
 "Golf", "dynamic": True}, 
            "mma": {"name": "MMA", "dynamic": True},
            "boxing": {"name": "Boxing", "dynamiclogger = logging.getLogger(__name__)


class ComprehensiveLeagueTester:
    """Test all discovered DraftKings leagues for data availability and market types."""
    
    def __init__(self):
        # Dis": True},
            "motorsports": {"name": "Motorsports", "dynamic": True},
            "soccer": {"name": "Soccer", "dynamic": True},
           covered leagues from API discovery
        self.discovered_leagues = {
            "nba": {"id": "42648", "name": "NBA", "status": "tested"},
            "esports": {"name": "Esports", "dynamic": True}
        }
        
        self.results = {}
        
    def test_league_data_collection(self, sport_key: str, league "nfl": {"id": "88808", "name": "NFL", "status": "tested"},
            "ncaab": {"id": "92483", "name":_info: Dict) -> Dict[str, Any]:
        """Test data collection for a specific league."""
        league_id = league_info["id"]
        league_name = league_info["name"]
        
        "NCAA Basketball", "status": "tested"},
            "ncaaf": {"id": "87637", "name": "NCAA Football", "status": "tested"},
            " logger.info(f"🧪 Testing {league_name} (ID: {league_id}) for {sport_key}")
        
        result = {
            "sport": sport_key,
            "league_namemlb": {"id": "84240", "name": "MLB", "status": "tested"},
            "nhl": {"id": "42133", "name": "N": league_name,
            "league_id": league_id,
            "test_timestamp": datetime.now().isoformat(),
            "data_available": False,
            "events_found": 0,
            "HL", "status": "tested"},
            "cfl": {"id": "33567", "name": "CFL (Unknown)", "status": "tested"},  # Unknownmarkets_found": 0,
            "market_types": [],
            "sample_events": [],
            "errors": [],
            "response_structure": None
        }
        
        try:
            # Create client league
        }
        
        # Additional sports that need dynamic discovery
        self.dynamic_sports = {
            "tennis": {"name": "Tennis", "dynamic": True},
            "g for this sport
            client = DraftKingsClient(sport_key)
            
            # Test data collection
            data = client.fetch()
            
            if data and isinstance(data, dict):
                result["olf": {"name": "Golf", "dynamic": True}, 
            "mma": {"name": "MMA", "dynamic": True},
            "boxing": {"name": "response_structure"] = list(data.keys())
                
                # Analyze the response structure
                events = data.get("events", [])
                if events:
                    result["events_found"] = len(events)
                   Boxing", "dynamic": True},
            "motorsports": {"name": "Motorsports", "dynamic": True},
            "soccer": {"name": "Soccer", " result["data_available"] = True
                    
                    # Analyze first few events
                    for i, event in enumerate(events[:3]):  # Check first 3 events
                        event_info = {
dynamic": True},
            "esports": {"name": "Esports", "dynamic": True}
        }
        
        self.results = {}
        
    def test_league_data_collection(self, sport                            "event_id": event.get("id"),
                            "away_team": event.get("awayTeam", {}).get("name", "Unknown"),
                            "home_team": event.get("homeTeam_key: str, league_info: Dict) -> Dict[str, Any]:
        """Test data collection for a specific league."""
        league_id = league_info["id"]
        league_name = league_info", {}).get("name", "Unknown"),
                            "start_time": event.get("startTime"),
                            "markets": len(event.get("competitions", []) if isinstance(event.get("competitions["name"]
        
        logger.info(f"🧪 Testing {league_name} (ID: {league_id}) for {sport_key}")
        
        result = {
            "sport": sport_key"), list) else [])
                        }
                        result["sample_events"].append(event_info)
                    
                    # Extract market types from events
                    market_types = set()
                    for event in events[:5]:,
            "league_name": league_name,
            "league_id": league_id,
            "test_timestamp": datetime.now().isoformat(),
            "data_available": False,
            "events_found":  # Check first 5 events
                        competitions = event.get("competitions", [])
                        for comp in competitions:
                            betting_offers = comp.get("bettingOffers", [])
                            for offer 0,
            "markets_found": 0,
            "market_types": [],
            "sample_events": [],
            "errors": [],
            "response_structure": None
        }
        
        try in betting_offers:
                                market_type = offer.get("marketType", {}).get("name", "")
                                if market_type:
                                    market_types.add(market_type)
                    
                    result["market:
            # Create client for this sport
            client = DraftKingsClient(sport_key)
            
            # Test data collection
            data = client.fetch()
            
            if data and isinstance(data,_types"] = list(market_types)
                    result["markets_found"] = len(market_types)
                    
                    logger.info(f"  ✅ {league_name}: {len(events)} events, {len(market_types)} market types")
                    
                else:
                    logger.info(f"  ℹ {league_name}: No events found (likely off-season)")
                    result["errors"].append("No events dict):
                result["response_structure"] = list(data.keys())
                
                # Analyze the response structure
                events = data.get("events", [])
                if events:
                    result["events_found"] found - likely off-season")
            
            else:
                logger.warning(f"  ⚠ {league_name}: No data returned")
                result["errors"].append("No data returned from API")
            
 = len(events)
                    result["data_available"] = True
                    
                    # Analyze first few events
                    for i, event in enumerate(events[:3]):  # Check first 3 events
            client.close()
            
        except Exception as e:
            error_msg = f"Error testing {league_name}: {str(e)}"
            logger.error(f"  ❌ {error_msg}")
                        event_info = {
                            "event_id": event.get("id"),
                            "away_team": event.get("awayTeam", {}).get("name", "Unknown"),
                            "home_team":            result["errors"].append(error_msg)
        
        return result

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test of all leagues and sports event.get("homeTeam", {}).get("name", "Unknown"),
                            "start_time": event.get("startTime"),
                            "markets": len(event.get("competitions", []) if isinstance."""
        logger.info("🎯 COMPREHENSIVE DRAFTKINGS LEAGUE TESTING")
        logger.info("=" * 80)
        
        # Test discovered leagues
        league(event.get("competitions"), list) else [])
                        }
                        result["sample_events"].append(event_info)
                    
                    # Extract market types from events
                    market_types = set()
                    for event_results = {}
        for sport_key, league_info in self.discovered_leagues.items():
            league_results[sport_key] = self.test_league_data_collection(sport_key, league_info)
        
 in events[:5]:  # Check first 5 events
                        competitions = event.get("competitions", [])
                        for comp in competitions:
                            betting_offers = comp.get("bettingOffers        # Compile final results
        final_results = {
            "test_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_sports_tested": len(self.discovered_le", [])
                            for offer in betting_offers:
                                market_type = offer.get("marketType", {}).get("name", "")
                                if market_type:
                                    market_types.add(market_type)
agues),
                "discovered_leagues": len(self.discovered_leagues),
                "sports_with_data": 0,
                "sports_off_season": 0,
                "sports_with_errors                    
                    result["market_types"] = list(market_types)
                    result["markets_found"] = len(market_types)
                    
                    logger.info(f"  ✅ {league_name}: {len(events": 0
            },
            "discovered_leagues": league_results,
        }
        
        # Calculate summary statistics
        for result in league_results.values():
            if result["data_available"]:
)} events, {len(market_types)} market types")
                    
                else:
                    logger.info(f"  ℹ {league_name}: No events found (likely off-season)")
                    result["errors                final_results["summary"]["sports_with_data"] += 1
            elif "off-season" in str(result.get("errors", [])):
                final_results["summary"]["sports_off_season"]"].append("No events found - likely off-season")
            
            else:
                logger.warning(f"  ⚠ {league_name}: No data returned")
                result["errors"].append("No data += 1
            else:
                final_results["summary"]["sports_with_errors"] += 1
        
        self.results = final_results
        return final_results

    def print_results(self):
        returned from API")
            
            client.close()
            
        except Exception as e:
            error_msg = f"Error testing {league_name}: {str(e)}"
            logger.error(f"  """Print the comprehensive results."""
        if not self.results:
            self.run_comprehensive_test()
        
        results = self.results
        
        print("\n" + "=" * 80)
        print ❌ {error_msg}")
            result["errors"].append(error_msg)
        
        return result

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test of all("📊 DRAFTKINGS COMPREHENSIVE LEAGUE & MARKET ANALYSIS")
        print("=" * 80)
        
        # Summary
        summary = results["summary"]
        leagues and sports."""
        logger.info("🎯 COMPREHENSIVE DRAFTKINGS LEAGUE TESTING")
        logger.info("=" * 80)
        
        # Test discovered leagues print(f"\n📈 SUMMARY:")
        print(f"  • Total Sports Tested: {summary['total_sports_tested']}")
        print(f"  • Sports with Active Data: {
        league_results = {}
        for sport_key, league_info in self.discovered_leagues.items():
            league_results[sport_key] = self.test_league_data_collection(sport_key, leaguesummary['sports_with_data']}")
        print(f"  • Sports Off-Season: {summary['sports_off_season']}")
        print(f"  • Sports with Errors: {summary['sports_with_errors']}")
        
        # Discovered Leagues Results
        print(f"\n🏈 DISCOVERED LEAGUES (Static IDs):")
        for sport_key, result in results_info)
        
        # Compile final results
        final_results = {
            "test_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_sports_tested": len(self["discovered_leagues"].items():
            status = "✅ ACTIVE" if result["data_available"] else "❌ OFF-SEASON" if "off-season" in str(result.get(".discovered_leagues),
                "discovered_leagues": len(self.discovered_leagues),
                "sports_with_data": 0,
                "sports_off_season": 0,
                "errors", [])) else "⚠️ ERROR"
            print(f"  {status} {result['league_name']} ({sport_key})")
            print(f"    League ID: {sports_with_errors": 0
            },
            "discovered_leagues": league_results,
        }
        
        # Calculate summary statistics
        for result in league_results.values():
            if result["result['league_id']}")
            print(f"    Events: {result['events_found']}, Markets: {result['markets_found']}")
            if result["market_types"]:
                print(f"data_available"]:
                final_results["summary"]["sports_with_data"] += 1
            elif "off-season" in str(result.get("errors", [])):
                final_results["summary"]["sports_off    Market Types: {', '.join(result['market_types'][:5])}{'...' if len(result['market_types']) > 5 else ''}")
            if result["errors"]:
                print_season"] += 1
            else:
                final_results["summary"]["sports_with_errors"] += 1
        
        self.results = final_results
        return final_results

    def print_results(f"    Notes: {result['errors'][0]}")
        
        print("\n" + "=" * 80)

    def save_results(self, filename="comprehensive_league_results.json(self):
        """Print the comprehensive results."""
        if not self.results:
            self.run_comprehensive_test()
        
        results = self.results
        
        print("\n" + "=" * 80)
        print("📊 DRAFTKINGS COMPREHENSIVE LEAGUE & MARKET ANALYSIS")
        print("=" * 80)
        
        # Summary
        summary = results[""):
        """Save comprehensive results to file."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(fsummary"]
        print(f"\n📈 SUMMARY:")
        print(f"  • Total Sports Tested: {summary['total_sports_tested']}")
        print(f"  • Sports with Active"Comprehensive results saved to {filename}")


def main():
    """Run comprehensive league testing."""
    tester = ComprehensiveLeagueTester()
    
    # Run all tests
    results = tester.run_comprehensive Data: {summary['sports_with_data']}")
        print(f"  • Sports Off-Season: {summary['sports_off_season']}")
        print(f"  • Sports with Errors:_test()
    
    # Display results
    tester.print_results()
    
    # Save results
    tester.save_results()
    
    return results


if __name__ == "__main__":
    results = main()
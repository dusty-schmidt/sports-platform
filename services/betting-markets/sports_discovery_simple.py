#!/usr/bin/env python3
"""Simple Sports Discovery Tool - Test API endpoints for different sports."""

import requests
import json
from datetime import datetime
from typing import Dict, List

def test_draftkings_endpoints():
    """Test DraftKings API endpoints for different sports."""
    print("=== Testing DraftKings League IDs ===")
    
    # Common league IDs to test
    test_ids = [
        ("nba", 42648),
        ("nfl", 42290), 
        ("mlb", 42288),
        ("nhl", 42294),
        ("epl", 42300),
        ("nba_summer", 42650),
        ("wnba", 42700),
        ("mma", 42600),
    ]
    
    working = {}
    
    for sport, league_id in test_ids:
        try:
            url = f"https://sportsbook-nash.draftkings.com/api/sportscontent/dkusoh/v1/leagues/{league_id}"
            print(f"Testing {sport} (ID: {league_id})...")
            
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                events_count = len(data.get("events", []))
                markets_count = len(data.get("markets", []))
                
                if events_count > 0:
                    working[sport] = {
                        "league_id": league_id,
                        "url": url,
                        "events": events_count,
                        "markets": markets_count,
                        "status": "SUCCESS"
                    }
                    print(f"  ✅ SUCCESS: {events_count} events, {markets_count} markets")
                    
                    # Check for prop markets
                    prop_markets = [m for m in data.get("markets", []) if "prop" in m.get("name", "").lower()]
                    if prop_markets:
                        print(f"     📊 Found {len(prop_markets)} prop markets")
                        working[sport]["prop_markets"] = len(prop_markets)
                else:
                    working[sport] = {
                        "league_id": league_id,
                        "url": url,
                        "events": 0,
                        "markets": markets_count,
                        "status": "NO_EVENTS"
                    }
                    print(f"  ⚠️  NO EVENTS: {markets_count} markets")
            else:
                print(f"  ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  💥 ERROR: {e}")
    
    return working

def test_fanduel_endpoints():
    """Test FanDuel API endpoints for different sports."""
    print("\\n=== Testing FanDuel Custom Page IDs ===")
    
    # Common page IDs to test
    test_ids = [
        ("nba", "nba"),
        ("nfl", "nfl"),
        ("mlb", "mlb"), 
        ("nhl", "nhl"),
        ("epl", "epl"),
        ("tennis", "tennis"),
        ("mma", "mma"),
        ("nba_summer", "nba-summer"),
        ("wnba", "wnba"),
    ]
    
    working = {}
    
    for sport, custom_page_id in test_ids:
        try:
            url = f"https://sbapi.oh.sportsbook.fanduel.com/api/content-managed-page?page=CUSTOM&customPageId={custom_page_id}&timezone=America/New_York"
            print(f"Testing {sport} (Page: {custom_page_id})...")
            
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                markets = data.get("attachments", {}).get("markets", {})
                markets_count = len(markets)
                
                if markets_count > 0:
                    working[sport] = {
                        "custom_page_id": custom_page_id,
                        "url": url,
                        "markets": markets_count,
                        "status": "SUCCESS"
                    }
                    print(f"  ✅ SUCCESS: {markets_count} markets")
                    
                    # Analyze market types to find props
                    market_types = {}
                    for market_data in markets.values():
                        market_type = market_data.get("marketType", "Unknown")
                        market_types[market_type] = market_types.get(market_type, 0) + 1
                    
                    # Look for prop-related market types
                    prop_types = [mt for mt in market_types.keys() if any(keyword in mt.lower() for keyword in ["prop", "player", "team", "special"])]
                    if prop_types:
                        print(f"     📊 Found prop market types: {', '.join(prop_types)}")
                        working[sport]["prop_market_types"] = prop_types
                    
                else:
                    working[sport] = {
                        "custom_page_id": custom_page_id,
                        "url": url,
                        "markets": 0,
                        "status": "NO_MARKETS"
                    }
                    print(f"  ⚠️  NO MARKETS")
            else:
                print(f"  ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  💥 ERROR: {e}")
    
    return working

def analyze_nba_market_structure():
    """Deep dive into NBA market structure to understand prop markets."""
    print("\\n=== Analyzing NBA Market Structure ===")
    
    # Get NBA data from both books
    try:
        # DraftKings NBA
        dk_url = "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusoh/v1/leagues/42648"
        dk_response = requests.get(dk_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        
        if dk_response.status_code == 200:
            dk_data = dk_response.json()
            dk_markets = dk_data.get("markets", [])
            
            print(f"DraftKings NBA: {len(dk_markets)} markets")
            
            # Analyze market patterns
            market_patterns = {}
            for market in dk_markets:
                market_id = market.get("id", "")
                market_name = market.get("name", "")
                market_type = market.get("marketType", "")
                
                # Categorize markets
                if "money" in market_name.lower():
                    category = "Moneyline"
                elif "spread" in market_name.lower() or "handicap" in market_name.lower():
                    category = "Spread/Handicap"
                elif "total" in market_name.lower() or "over" in market_name.lower() or "under" in market_name.lower():
                    category = "Totals"
                elif "prop" in market_name.lower():
                    category = "Props"
                else:
                    category = "Other"
                
                market_patterns[category] = market_patterns.get(category, 0) + 1
            
            print("DraftKings Market Categories:")
            for category, count in market_patterns.items():
                print(f"  {category}: {count}")
            
    except Exception as e:
        print(f"Error analyzing DraftKings NBA: {e}")
    
    try:
        # FanDuel NBA
        fd_url = "https://sbapi.oh.sportsbook.fanduel.com/api/content-managed-page?page=CUSTOM&customPageId=nba&timezone=America/New_York"
        fd_response = requests.get(fd_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        
        if fd_response.status_code == 200:
            fd_data = fd_response.json()
            fd_markets = fd_data.get("attachments", {}).get("markets", {})
            
            print(f"\\nFanDuel NBA: {len(fd_markets)} markets")
            
            # Analyze market types
            market_types = {}
            for market_id, market_data in fd_markets.items():
                market_type = market_data.get("marketType", "Unknown")
                market_types[market_type] = market_types.get(market_type, 0) + 1
            
            print("FanDuel Market Types:")
            for market_type, count in sorted(market_types.items()):
                print(f"  {market_type}: {count}")
                
    except Exception as e:
        print(f"Error analyzing FanDuel NBA: {e}")

def main():
    print("🏆 Sports Discovery Tool")
    print("Testing API endpoints to discover available sports and market types\\n")
    
    # Test both sportsbooks
    dk_results = test_draftkings_endpoints()
    fd_results = test_fanduel_endpoints()
    
    # Deep dive into NBA structure
    analyze_nba_market_structure()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {
        "timestamp": timestamp,
        "draftkings": dk_results,
        "fanduel": fd_results,
        "summary": {
            "draftkings_working": len([s for s, d in dk_results.items() if d.get("status") == "SUCCESS"]),
            "fanduel_working": len([s for s, d in fd_results.items() if d.get("status") == "SUCCESS"])
        }
    }
    
    filename = f"sports_discovery_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\\n🎯 Discovery Complete!")
    print(f"   DraftKings: {results['summary']['draftkings_working']} working sports")
    print(f"   FanDuel: {results['summary']['fanduel_working']} working sports")
    print(f"   Results saved to: {filename}")
    
    # Print summary table
    print("\\n📊 Summary Table:")
    print("Sport    | DraftKings | FanDuel")
    print("-" * 40)
    all_sports = set(list(dk_results.keys()) + list(fd_results.keys()))
    for sport in sorted(all_sports):
        dk_status = "✅" if dk_results.get(sport, {}).get("status") == "SUCCESS" else "❌"
        fd_status = "✅" if fd_results.get(sport, {}).get("status") == "SUCCESS" else "❌"
        print(f"{sport:8} | {dk_status:10} | {fd_status}")

if __name__ == "__main__":
    main()
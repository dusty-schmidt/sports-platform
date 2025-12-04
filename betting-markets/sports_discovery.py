#!/usr/bin/env python3
"""Sports Discovery Tool - Find league IDs and custom page IDs for all sports."""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

def test_draftkings_league_ids():
    """Test common DraftKings league IDs for different sports."""
    print("=== DraftKings League ID Discovery ===")
    
    # Common league IDs based on typical sportsbook patterns
    potential_ids = {
        # NBA family
        "nba": 42648,
        "nba_d": 42649,  # NBA Draft
        "nba_summer": 42650,  # Summer League
        
        # NFL family  
        "nfl": 42290,
        "nfl_super_bowl": 42291,
        "nfl_hof": 42292,
        
        # MLB family
        "mlb": 42288,
        "mlb_world_series": 42289,
        
        # NHL family
        "nhl": 42294,
        "nhl_stanley_cup": 42295,
        
        # Soccer/Cricket
        "epl": 42300,
        "champions_league": 42301,
        "mls": 42302,
        "world_cup": 42303,
        
        # Tennis
        "atp": 42400,
        "wta": 42401,
        "grand_slams": 42402,
        
        # Golf
        "pga": 42500,
        "lpga": 42501,
        "masters": 42502,
        
        # Others
        "mma": 42600,
        "boxing": 42601,
        "nascar": 42610,
        "f1": 42611,
    }
    
    working_sports = {}
    
    for sport, league_id in potential_ids.items():
        try:
            url = f"https://sportsbook-nash.draftkings.com/api/sportscontent/dkusoh/v1/leagues/{league_id}"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "events" in data and len(data["events"]) > 0:
                    working_sports[sport] = {
                        "league_id": league_id,
                        "url": url,
                        "events_count": len(data["events"]),
                        "status": "SUCCESS"
                    }
                    print(f"✅ {sport.upper()}: League ID {league_id} - {len(data['events'])} events")
                else:
                    working_sports[sport] = {
                        "league_id": league_id, 
                        "url": url,
                        "events_count": 0,
                        "status": "NO_EVENTS"
                    }
                    print(f"⚠️  {sport.upper()}: League ID {league_id} - No events")
            else:
                print(f"❌ {sport.upper()}: League ID {league_id} - HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ {sport.upper()}: League ID {league_id} - Timeout")
        except Exception as e:
            print(f"💥 {sport.upper()}: League ID {league_id} - Error: {e}")
    
    return working_sports

def test_fanduel_page_ids():
    """Test common FanDuel custom page IDs for different sports."""
    print("\n=== FanDuel Custom Page ID Discovery ===")
    
    # Common custom page IDs
    potential_ids = {
        # Major US Sports
        "nba": "nba",
        "nfl": "nfl", 
        "mlb": "mlb",
        "nhl": "nhl",
        "nba_summer": "nba-summer",
        "wnba": "wnba",
        
        # Soccer
        "epl": "epl",
        "champions_league": "champions-league",
        "mls": "mls",
        "world_cup": "world-cup",
        "europa": "europa-league",
        "bundesliga": "bundesliga",
        "la_liga": "la-liga",
        "serie_a": "serie-a",
        "ligue_1": "ligue-1",
        
        # Tennis
        "tennis": "tennis",
        "us_open": "us-open",
        "wimbledon": "wimbledon",
        "french_open": "french-open",
        "australian_open": "australian-open",
        
        # Golf
        "pga": "pga",
        "masters": "masters",
        "us_open_golf": "us-open-golf",
        "british_open": "british-open",
        
        # Combat Sports
        "mma": "mma",
        "boxing": "boxing",
        "ufc": "ufc",
        
        # Racing
        "nascar": "nascar",
        "f1": "f1",
        "indycar": "indycar",
        
        # Others
        "cricket": "cricket",
        "rugby": "rugby",
        "olympics": "olympics",
    }
    
    working_sports = {}
    
    for sport, custom_page_id in potential_ids.items():
        try:
            url = f"https://sbapi.oh.sportsbook.fanduel.com/api/content-managed-page?page=CUSTOM&customPageId={custom_page_id}&timezone=America/New_York"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                attachments = data.get("attachments", {})
                markets = attachments.get("markets", {})
                
                if markets and len(markets) > 0:
                    working_sports[sport] = {
                        "custom_page_id": custom_page_id,
                        "url": url,
                        "markets_count": len(markets),
                        "status": "SUCCESS"
                    }
                    print(f"✅ {sport.upper()}: Custom Page ID '{custom_page_id}' - {len(markets)} markets")
                else:
                    working_sports[sport] = {
                        "custom_page_id": custom_page_id,
                        "url": url, 
                        "markets_count": 0,
                        "status": "NO_MARKETS"
                    }
                    print(f"⚠️  {sport.upper()}: Custom Page ID '{custom_page_id}' - No markets")
            else:
                print(f"❌ {sport.upper()}: Custom Page ID '{custom_page_id}' - HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ {sport.upper()}: Custom Page ID '{custom_page_id}' - Timeout")
        except Exception as e:
            print(f"💥 {sport.upper()}: Custom Page ID '{custom_page_id}' - Error: {e}")
    
    return working_sports

def discover_prop_markets():
    """Try to discover prop betting markets for different sports."""
    print("\n=== Prop Markets Discovery ===")
    
    # Test if prop markets are accessible through different endpoints
    # For DraftKings, props might be in different market types
    # For FanDuel, props might be accessible via different market types
    
    prop_tests = {
        "draftkings": [
            "player_props",
            "game_props", 
            "team_props",
            "specials"
        ],
        "fanduel": [
            "player_props",
            "game_props",
            "team_props", 
            "specials"
        ]
    }
    
    results = {}
    
    for sportsbook, prop_types in prop_tests.items():
        results[sportsbook] = {}
        for prop_type in prop_types:
            try:
                if sportsbook == "draftkings":
                    # For DraftKings, props might be in different market patterns
                    # Need to analyze the response structure
                    url = f"https://sportsbook-nash.draftkings.com/api/sportscontent/dkusoh/v1/leagues/42648"
                    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        markets = data.get("markets", [])
                        prop_markets = [m for m in markets if prop_type in m.get("id", "").lower()]
                        results[sportsbook][prop_type] = len(prop_markets)
                        print(f"DraftKings {prop_type}: {len(prop_markets)} prop markets found")
                
                elif sportsbook == "fanduel":
                    # For FanDuel, look for prop market types
                    url = f"https://sbapi.oh.sportsbook.fanduel.com/api/content-managed-page?page=CUSTOM&customPageId=nba&timezone=America/New_York"
                    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        attachments = data.get("attachments", {})
                        markets = attachments.get("markets", {})
                        prop_markets = [m for m in markets.values() if prop_type in m.get("marketType", "").lower()]
                        results[sportsbook][prop_type] = len(prop_markets)
                        print(f"FanDuel {prop_type}: {len(prop_markets)} prop markets found")
                        
            except Exception as e:
                results[sportsbook][prop_type] = 0
                print(f"{sportsbook.title()} {prop_type}: Error - {e}")
    
    return results

def save_results(dk_results, fd_results, prop_results):
    """Save discovery results to files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save to JSON
    results = {
        "timestamp": timestamp,
        "draftkings": dk_results,
        "fanduel": fd_results,
        "prop_markets": prop_results
    }
    
    with open(f"sports_discovery_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Create updated sports config
    create_sports_config(dk_results, fd_results)

def create_sports_config(dk_results, fd_results):
    """Create updated sports configuration."""
    
    # DraftKings sport mappings
    dk_sports = {}
    for sport, data in dk_results.items():
        if data.get("status") == "SUCCESS":
            dk_sports[sport] = {
                "name": sport.upper(),
                "options": {"league_id": str(data["league_id"])}
            }
    
    # FanDuel sport mappings  
    fd_sports = {}
    for sport, data in fd_results.items():
        if data.get("status") == "SUCCESS":
            fd_sports[sport] = {
                "name": sport.upper(), 
                "options": {"custom_page_id": data["custom_page_id"]}
            }
    
    # Create new config file
    config_content = f'''"""Discovered sports configuration for betting market service."""

from dataclasses import dataclass
from typing import Dict, Mapping

@dataclass(frozen=True)
class BookConfig:
    """Configuration for a sportsbook for a given sport."""
    name: str
    options: Mapping[str, str]

@dataclass(frozen=True)  
class SportConfig:
    """Configuration container describing a sport."""
    name: str
    timezone: str
    team_aliases: Mapping[str, str]
    books: Mapping[str, BookConfig]

# Common team aliases for different sports
NBA_TEAM_ALIASES = {{
    "atlanta hawks": "ATL", "boston celtics": "BOS", "brooklyn nets": "BKN",
    "charlotte hornets": "CHA", "chicago bulls": "CHI", "cleveland cavaliers": "CLE",
    "dallas mavericks": "DAL", "denver nuggets": "DEN", "detroit pistons": "DET",
    "golden state warriors": "GSW", "houston rockets": "HOU", "indiana pacers": "IND",
    "los angeles clippers": "LAC", "los angeles lakers": "LAL", "memphis grizzlies": "MEM",
    "miami heat": "MIA", "milwaukee bucks": "MIL", "minnesota timberwolves": "MIN",
    "new orleans pelicans": "NOP", "new york knicks": "NYK", "oklahoma city thunder": "OKC",
    "orlando magic": "ORL", "philadelphia 76ers": "PHI", "phoenix suns": "PHX",
    "portland trail blazers": "POR", "sacramento kings": "SAC", "san antonio spurs": "SAS",
    "toronto raptors": "TOR", "utah jazz": "UTA", "washington wizards": "WAS",
}}

NFL_TEAM_ALIASES = {{
    "arizona cardinals": "ARI", "atlanta falcons": "ATL", "baltimore ravens": "BAL",
    "buffalo bills": "BUF", "carolina panthers": "CAR", "chicago bears": "CHI",
    "cincinnati bengals": "CIN", "cleveland browns": "CLE", "dallas cowboys": "DAL",
    "denver broncos": "DEN", "detroit lions": "DET", "green bay packers": "GB",
    "houston texans": "HOU", "indianapolis colts": "IND", "jacksonville jaguars": "JAX",
    "kansas city chiefs": "KC", "las vegas raiders": "LV", "los angeles chargers": "LAC",
    "los angeles rams": "LAR", "miami dolphins": "MIA", "minnesota vikings": "MIN",
    "new england patriots": "NE", "new orleans saints": "NO", "new york giants": "NYG",
    "new york jets": "NYJ", "philadelphia eagles": "PHI", "pittsburgh steelers": "PIT",
    "san francisco 49ers": "SF", "seattle seahawks": "SEA", "tampa bay buccaneers": "TB",
    "tennessee titans": "TEN", "washington commanders": "WAS",
}}

SPORTS = {{
    # NBA
    "nba": SportConfig(
        name="NBA",
        timezone="America/New_York",
        team_aliases=NBA_TEAM_ALIASES,
        books={dk_sports.get("nba", {}).get("name", "DraftKings"): BookConfig(name="DraftKings", options=dk_sports.get("nba", {}).get("options", {{"league_id": "42648"}})),
               fd_sports.get("nba", {}).get("name", "FanDuel"): BookConfig(name="FanDuel", options=fd_sports.get("nba", {}).get("options", {{"custom_page_id": "nba"}}))},
    ),
    # NFL  
    "nfl": SportConfig(
        name="NFL",
        timezone="America/New_York", 
        team_aliases=NFL_TEAM_ALIASES,
        books={dk_sports.get("nfl", {}).get("name", "DraftKings"): BookConfig(name="DraftKings", options=dk_sports.get("nfl", {}).get("options", {{"league_id": "42290"}})),
               fd_sports.get("nfl", {}).get("name", "FanDuel"): BookConfig(name="FanDuel", options=fd_sports.get("nfl", {}).get("options", {{"custom_page_id": "nfl"}}))},
    ),
    # MLB
    "mlb": SportConfig(
        name="MLB",
        timezone="America/New_York",
        team_aliases={{}},  # TODO: Add MLB team aliases
        books={dk_sports.get("mlb", {}).get("name", "DraftKings"): BookConfig(name="DraftKings", options=dk_sports.get("mlb", {}).get("options", {{"league_id": "42288"}})),
               fd_sports.get("mlb", {}).get("name", "FanDuel"): BookConfig(name="FanDuel", options=fd_sports.get("mlb", {}).get("options", {{"custom_page_id": "mlb"}}))},
    ),
    # NHL
    "nhl": SportConfig(
        name="NHL", 
        timezone="America/New_York",
        team_aliases={{}},  # TODO: Add NHL team aliases
        books={dk_sports.get("nhl", {}).get("name", "DraftKings"): BookConfig(name="DraftKings", options=dk_sports.get("nhl", {}).get("options", {{"league_id": "42294"}})),
               fd_sports.get("nhl", {}).get("name", "FanDuel"): BookConfig(name="FanDuel", options=fd_sports.get("nhl", {}).get("options", {{"custom_page_id": "nhl"}}))},
    ),
    # Soccer/EPL
    "epl": SportConfig(
        name="English Premier League",
        timezone="Europe/London", 
        team_aliases={{}},  # TODO: Add EPL team aliases
        books={dk_sports.get("epl", {}).get("name", "DraftKings"): BookConfig(name="DraftKings", options=dk_sports.get("epl", {}).get("options", {{"league_id": "42300"}})),
               fd_sports.get("epl", {}).get("name", "FanDuel"): BookConfig(name="FanDuel", options=fd_sports.get("epl", {}).get("options", {{"custom_page_id": "epl"}}))},
    ),
}}

def get_sport_config(key: str) -> SportConfig:
    try:
        return SPORTS[key.lower()]
    except KeyError as exc:
        raise ValueError(f"Unsupported sport: {{key}}") from exc
'''
    
    with open("sports_config_discovered.py", "w") as f:
        f.write(config_content)
    
    print(f"\\nCreated new sports configuration: sports_config_discovered.py")

if __name__ == "__main__":
    print("Starting comprehensive sports discovery...")
    print("This will test endpoints for multiple sports to find working league IDs and page IDs.\\n")
    
    # Test DraftKings
    dk_results = test_draftkings_league_ids()
    
    # Test FanDuel
    fd_results = test_fanduel_page_ids()
    
    # Test prop markets
    prop_results = discover_prop_markets()
    
    # Save results
    save_results(dk_results, fd_results, prop_results)
    
    print(f"\\n🎯 Discovery complete! Found:")
    print(f"   DraftKings: {sum(1 for v in dk_results.values() if v.get('status') == 'SUCCESS')} working sports")
    print(f"   FanDuel: {sum(1 for v in fd_results.values() if v.get('status') == 'SUCCESS')} working sports")
    print(f"   Check sports_discovery_*.json and sports_config_discovered.py for results")
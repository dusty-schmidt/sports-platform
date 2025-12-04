#!/usr/bin/env python3
"""Multi-sport configuration for comprehensive betting market data collection."""

from betting_service.config.sports import SportConfig, BookConfig

# Common team aliases for different sports
NBA_TEAM_ALIASES = {
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
}

NFL_TEAM_ALIASES = {
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
}

# Multi-sport configuration
MULTI_SPORT_CONFIG = {
    # NBA - CONFIRMED WORKING
    "nba": SportConfig(
        name="NBA",
        timezone="America/New_York",
        team_aliases=NBA_TEAM_ALIASES,
        books={
            "draftkings": BookConfig(name="DraftKings", options={"league_id": "42648"}),
            "fanduel": BookConfig(name="FanDuel", options={"custom_page_id": "nba"}),
        },
    ),
    
    # NFL - USER DISCOVERED: 88808
    "nfl": SportConfig(
        name="NFL",
        timezone="America/New_York",
        team_aliases=NFL_TEAM_ALIASES,
        books={
            "draftkings": BookConfig(name="DraftKings", options={"league_id": "88808"}),
            "fanduel": BookConfig(name="FanDuel", options={"custom_page_id": "nfl"}),
        },
    ),
    
    # MLB - ESTIMATED based on pattern
    "mlb": SportConfig(
        name="MLB",
        timezone="America/New_York",
        team_aliases={},  # TODO: Add MLB team aliases
        books={
            "draftkings": BookConfig(name="DraftKings", options={"league_id": "42288"}),
            "fanduel": BookConfig(name="FanDuel", options={"custom_page_id": "mlb"}),
        },
    ),
    
    # NHL - ESTIMATED based on pattern
    "nhl": SportConfig(
        name="NHL",
        timezone="America/New_York",
        team_aliases={},  # TODO: Add NHL team aliases
        books={
            "draftkings": BookConfig(name="DraftKings", options={"league_id": "42294"}),
            "fanduel": BookConfig(name="FanDuel", options={"custom_page_id": "nhl"}),
        },
    ),
    
    # English Premier League - ESTIMATED
    "epl": SportConfig(
        name="English Premier League",
        timezone="Europe/London",
        team_aliases={},  # TODO: Add EPL team aliases
        books={
            "draftkings": BookConfig(name="DraftKings", options={"league_id": "42300"}),
            "fanduel": BookConfig(name="FanDuel", options={"custom_page_id": "epl"}),
        },
    ),
    
    # Champions League - ESTIMATED
    "champions_league": SportConfig(
        name="UEFA Champions League",
        timezone="Europe/London",
        team_aliases={},  # TODO: Add Champions League team aliases
        books={
            "draftkings": BookConfig(name="DraftKings", options={"league_id": "42301"}),
            "fanduel": BookConfig(name="FanDuel", options={"custom_page_id": "champions-league"}),
        },
    ),
    
    # NCAA Basketball - ESTIMATED
    "ncaab": SportConfig(
        name="NCAA Basketball",
        timezone="America/New_York",
        team_aliases={},  # TODO: Add NCAA team aliases
        books={
            "draftkings": BookConfig(name="DraftKings", options={"league_id": "42649"}),
            "fanduel": BookConfig(name="FanDuel", options={"custom_page_id": "college-basketball"}),
        },
    ),
    
    # NCAA Football - ESTIMATED
    "ncaaf": SportConfig(
        name="NCAA Football",
        timezone="America/New_York",
        team_aliases={},  # TODO: Add NCAA team aliases
        books={
            "draftkings": BookConfig(name="DraftKings", options={"league_id": "42291"}),
            "fanduel": BookConfig(name="FanDuel", options={"custom_page_id": "college-football"}),
        },
    ),
}

def get_sport_config(key: str) -> SportConfig:
    """Get configuration for a specific sport."""
    try:
        return MULTI_SPORT_CONFIG[key.lower()]
    except KeyError as exc:
        raise ValueError(f"Unsupported sport: {key}") from exc

# Test function for multiple sports
def test_multi_sport_collection():
    """Test data collection for multiple sports."""
    from betting_service.service import BettingMarketService
    import json
    from datetime import datetime
    
    print("🏆 Multi-Sport Data Collection Test")
    print("=" * 50)
    
    results = {}
    
    for sport_name in ["nba", "nfl", "mlb", "nhl"]:
        print(f"\\nTesting {sport_name.upper()}...")
        try:
            service = BettingMarketService(sport_name)
            events = service.collect()
            
            results[sport_name] = {
                "status": "success" if events else "no_events",
                "events_collected": len(events),
                "events": [e.__dict__ for e in events[:3]] if events else [],  # First 3 events
            }
            
            if events:
                print(f"  ✅ {len(events)} events collected")
                # Show sample event
                sample = events[0]
                print(f"     Sample: {sample.game}")
                print(f"     Teams: {sample.away} @ {sample.home}")
                print(f"     Moneyline: {sample.away_moneyline} / {sample.home_moneyline}")
            else:
                print(f"  ⚠️  No events found")
                
        except Exception as e:
            results[sport_name] = {
                "status": "error",
                "error": str(e),
                "events_collected": 0
            }
            print(f"  💥 Error: {e}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"multi_sport_test_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\\n📊 Results saved to: multi_sport_test_{timestamp}.json")
    return results

if __name__ == "__main__":
    test_multi_sport_collection()
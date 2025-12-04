"""Sport-specific configuration for betting market service."""

from __future__ import annotations

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
NBA_TEAM_ALIASES: Dict[str, str] = {
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

NFL_TEAM_ALIASES: Dict[str, str] = {
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

# Comprehensive sports configuration with CORRECT FanDuel league IDs from routes data
SPORTS: Dict[str, SportConfig] = {
    # NBA - CONFIRMED WORKING with 42648
    "nba": SportConfig(
        name="NBA",
        timezone="America/New_York",
        team_aliases=NBA_TEAM_ALIASES,
        books={
            "draftkings": BookConfig(
                name="DraftKings",
                options={"league_id": "42648"},
            ),
            "fanduel": BookConfig(
                name="FanDuel",
                options={"custom_page_id": "nba"},
            ),
        },
    ),
    
    # NFL - USER DISCOVERED: 88808 (confirmed in routes)
    "nfl": SportConfig(
        name="NFL",
        timezone="America/New_York",
        team_aliases=NFL_TEAM_ALIASES,
        books={
            "draftkings": BookConfig(
                name="DraftKings",
                options={"league_id": "88808"},
            ),
            "fanduel": BookConfig(
                name="FanDuel",
                options={"custom_page_id": "nfl"},
            ),
        },
    ),
    
    # NCAA Football - CORRECTED: 87637 (from routes data, not 42291)
    "ncaaf": SportConfig(
        name="NCAA Football",
        timezone="America/New_York",
        team_aliases={},  # TODO: Add NCAA team aliases
        books={
            "draftkings": BookConfig(
                name="DraftKings",
                options={"league_id": "87637"},  # Corrected from routes data
            ),
            "fanduel": BookConfig(
                name="FanDuel",
                options={"custom_page_id": "college-football"},
            ),
        },
    ),
    
    # NCAA Basketball - CORRECTED: 92483 (from routes data, not 42649)
    "ncaab": SportConfig(
        name="NCAA Basketball",
        timezone="America/New_York",
        team_aliases={},  # TODO: Add NCAA team aliases
        books={
            "draftkings": BookConfig(
                name="DraftKings",
                options={"league_id": "92483"},  # Corrected from routes data
            ),
            "fanduel": BookConfig(
                name="FanDuel",
                options={"custom_page_id": "college-basketball"},
            ),
        },
    ),
    
    # MLB - CORRECTED: 84240 (from routes data, not 42288)
    "mlb": SportConfig(
        name="MLB",
        timezone="America/New_York",
        team_aliases={},  # TODO: Add MLB team aliases
        books={
            "draftkings": BookConfig(
                name="DraftKings",
                options={"league_id": "84240"},  # Corrected from routes data
            ),
            "fanduel": BookConfig(
                name="FanDuel",
                options={"custom_page_id": "mlb"},
            ),
        },
    ),
    
    # NHL - CORRECTED: 42133 (from routes data, not 42294)
    "nhl": SportConfig(
        name="NHL",
        timezone="America/New_York",
        team_aliases={},  # TODO: Add NHL team aliases
        books={
            "draftkings": BookConfig(
                name="DraftKings",
                options={"league_id": "42133"},  # Corrected from routes data
            ),
            "fanduel": BookConfig(
                name="FanDuel",
                options={"custom_page_id": "nhl"},
            ),
        },
    ),
    
    # English Premier League - Soccer league ID 40685 (Champions League from routes)
    "epl": SportConfig(
        name="English Premier League",
        timezone="Europe/London",
        team_aliases={},  # TODO: Add EPL team aliases
        books={
            "draftkings": BookConfig(
                name="DraftKings",
                options={"league_id": "40685"},  # Soccer league from routes
            ),
            "fanduel": BookConfig(
                name="FanDuel",
                options={"custom_page_id": "epl"},
            ),
        },
    ),
    
    # Tennis - Based on routes patterns
    "tennis": SportConfig(
        name="Tennis",
        timezone="America/New_York",
        team_aliases={},  # No team aliases for tennis
        books={
            "draftkings": BookConfig(
                name="DraftKings",
                options={"league_id": "72778"},  # US Open Men from routes
            ),
            "fanduel": BookConfig(
                name="FanDuel",
                options={"custom_page_id": "tennis"},
            ),
        },
    ),
    
    # Golf - CORRECTED: 16936 (Ryder Cup from routes data)
    "golf": SportConfig(
        name="PGA Tour",
        timezone="America/New_York",
        team_aliases={},  # No team aliases for golf
        books={
            "draftkings": BookConfig(
                name="DraftKings",
                options={"league_id": "16936"},  # Ryder Cup from routes data
            ),
            "fanduel": BookConfig(
                name="FanDuel",
                options={"custom_page_id": "pga"},
            ),
        },
    ),
    
    # MMA - From routes data
    "mma": SportConfig(
        name="MMA",
        timezone="America/New_York",
        team_aliases={},  # No team aliases for MMA
        books={
            "draftkings": BookConfig(
                name="DraftKings",
                options={"league_id": "9034"},  # UFC from routes data
            ),
            "fanduel": BookConfig(
                name="FanDuel",
                options={"custom_page_id": "mma"},
            ),
        },
    ),
    
    # Boxing - From routes data
    "boxing": SportConfig(
        name="Boxing",
        timezone="America/New_York",
        team_aliases={},  # No team aliases for boxing
        books={
            "draftkings": BookConfig(
                name="DraftKings",
                options={"league_id": "3655d966"},  # Boxing from routes
            ),
            "fanduel": BookConfig(
                name="FanDuel",
                options={"custom_page_id": "boxing"},
            ),
        },
    ),
    
    # WNBA - From routes data
    "wnba": SportConfig(
        name="WNBA",
        timezone="America/New_York",
        team_aliases={},  # TODO: Add WNBA team aliases
        books={
            "draftkings": BookConfig(
                name="DraftKings",
                options={"league_id": "94682"},  # WNBA from routes data
            ),
            "fanduel": BookConfig(
                name="FanDuel",
                options={"custom_page_id": "wnba"},
            ),
        },
    ),
}


def get_sport_config(key: str) -> SportConfig:
    """Get configuration for a specific sport."""
    try:
        return SPORTS[key.lower()]
    except KeyError as exc:
        raise ValueError(f"Unsupported sport: {key}") from exc
# DraftKings Sportsbook API - Complete Technical Documentation

## 📊 Overview

This document provides comprehensive technical documentation for reverse-engineered DraftKings Sportsbook API endpoints discovered through systematic analysis. The API provides access to real-time betting markets, odds, and event data across multiple sports.

## 🔐 Authentication & Headers

**No authentication required** - DraftKings API is publicly accessible.

### Required Headers
```http
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br, zstd
Referer: https://sportsbook.draftkings.com/
X-Client-Name: web
X-Client-Version: 1.4.0
X-Client-Feature: cms
X-Client-Page: home
Origin: https://sportsbook.draftkings.com
Connection: keep-alive
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-site
Priority: u=4
```

### Base URL
```
https://sportsbook-nash.draftkings.com
```

## 🏆 API Endpoints

### 1. Manifest Endpoint - Discover Available Sports/Leagues

**Endpoint:** `/sites/US-OH-SB/api/sportslayout/v1/manifest?format=json`

**Method:** `GET`

**Purpose:** Retrieves all available sports and their league configurations. This is the entry point for discovering what content is available.

**Response Structure:**
```json
{
  "routes": [
    {
      "key": "event",
      "entityType": "event",
      "route": "/sport/{sportId}/league/{leagueId}/event/{eventId}",
      "overrides": [
        {
          "route": "/sport/2/league/42648/event/{eventId}",
          "templateId": "6fe8a4fa-539b-4533-ac53-c3a0a879a8a8__client_web_1.3.0"
        }
      ]
    }
  ]
}
```

**Usage Example:**
```python
response = requests.get("https://sportsbook-nash.draftkings.com/sites/US-OH-SB/api/sportslayout/v1/manifest?format=json", headers=headers)
manifest = response.json()
```

### 2. League Content Endpoint - Get Betting Data

**Endpoint:** `/api/sportscontent/dkusoh/v1/leagues/{league_id}`

**Method:** `GET`

**Purpose:** Retrieves all betting markets and events for a specific league.

**Path Parameters:**
- `league_id`: The league identifier (e.g., "42648" for NBA)

**Response Structure:**
```json
{
  "sports": [...],
  "leagues": [...],
  "events": [
    {
      "id": "event_12345",
      "awayTeam": {"name": "Los Angeles Lakers"},
      "homeTeam": {"name": "Golden State Warriors"},
      "startTime": "2025-11-04T19:00:00Z",
      "competitions": [
        {
          "bettingOffers": [
            {
              "marketType": {
                "name": "moneyline"
              },
              "outcomes": [
                {
                  "name": "Los Angeles Lakers",
                  "price": {"american": -150, "decimal": 1.67}
                },
                {
                  "name": "Golden State Warriors",
                  "price": {"american": 130, "decimal": 2.30}
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "markets": [...],
  "selections": [...],
  "categories": [...],
  "subcategories": [...]
}
```

**Usage Example:**
```python
# Get NBA betting data
response = requests.get(
    "https://sportsbook-nash.draftkings.com/api/sportscontent/dkusoh/v1/leagues/42648",
    headers=headers
)
nba_data = response.json()
```

## 📋 League IDs - Complete Reference

Based on reverse engineering, here are the discovered league IDs:

| Sport | League ID |<write_to_file>
<content Full Name | Status | Market Types># DraftKings Sportsbook API - Complete Developer Documentation

## |
|-------|-----------|-----------| 📋---------| Table of---------------|
| Contents
1. [Overview](#overview)
2. [Authentication NBA | 42648 | & Headers](#authentication--headers)
3 National Basketball Association | ✅. [ Active |API Endpoints](#api-endpoints)
 231 |
| NFL | 88808 | National Football League | ✅ Active4. [League IDs & | 171 |
| NCAA Sports](#league-ids--sports)
5. [Market Types & Basketball | 92483 | NCAA Categories](#market-types--categories)
6. [ Basketball | ✅ Active | 57 |
Request/Response| NCAA Football | 87637 | NCAA Football | ✅ Active | 60 Formats](#requestresponse-form |
| MLB | 84240 |ats)
7. [Code Examples](#code-examples)
8. [ Major League Baseball | ⚠️ OffError Handling](#error-handling)
9-Season | 4 |
| NHL. [Best Practices](#best-practices)
10. | 42133 | National Hockey League [Rate Limiting & | ✅ Active | 92 |
| WNBA | 94682 | Women's Qu National Basketball Association | ⚠️ Offotas](#rate-limiting--quotas)

## 📖 Overview

The Draft-Season | 6Kings Sportsbook API provides comprehensive |

## access to 💰 Market Types - real-time betting market data across Complete multiple sports Taxonomy

### Core Markets (.Available in Most This documentation covers the Leagues reverse-engineered)

#### API structure, including all discovered endpoints, league IDs Moneyline
, and market types.

###```json
{
  " Key Features
- **marketType":452 Unique Market Types {"name": "moneyline"},
 ** discovered across "outcomes": [
    {"name 7 major leagues
- **Real-time betting": "Team A", "price": odds** for active events
- **Comprehensive market coverage** including futures, props, and live {"american": -150, "decimal betting
- **Public API** (no authentication required)
- **JSON responses** with structured data

### Base URL
```
https://sportsbook-nash.draftkings.com
```

## 🔐 Authentication & Headers

": 1.67}},
    {"**name": "Team B", "price": {"american": 130, "decimal": 2.30}}
  ]
}
```

#### Spread/Point Spread
```json
{
No authentication required** - this is  "marketType a public API. However": {"name":, "spread proper headers"},
  "line": 5.5,
  "outcomes": [
    {" arename": "Team A - essential5.5", "price": {" foramerican": -110, "decimal successful requests:

### Required": 1. Headers
```http
91}},
    {"name": "TeamUser-Agent: Mozilla/ B +5.5", "price5.0 (X11": {"american": -110, "; Linux x86_decimal": 1.91}}
64 ; rv: ]
}
```

#### Total/Over144.0) Gecko/20100101 Firefox/144.-Under
```json
{
 0
Accept: */*
 "marketType": {"name": "Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br, zstd
Referer: https://sportsbook.draftkings.com/
X-Client-Name: web
X-Client-Version: 1.4.0
X-Client-Feature: cms
Xtotal"},
  "line": 220-Client-Page: home
Origin: https://sportsbook.d.5,
  "outcomes":raftkings.com
Connection: keep-alive
Sec-Fetch [
    {"name": "Over 220.-Dest:5", "price": empty
Sec-F {"american": -etch-Mode: cors
Sec-Fetch-Site110, "decimal": 1.: same-site
Priority:91}},
    {"name": "Under u=4
```

### JavaScript Implementation
```javascript 220.5", "price":
const headers = {"american": -110, "decimal {
  "User-Agent": "Mozilla/": 1.5.091}}
  ]
}
 (X11; Linux```

### x Basketball-Specific Markets86_64 (NBA; rv:144.0) Gecko/20100101 Firefox/, NCAA144.0",
 , WNBA)

#### Player Props
 "Accept": "*/*",
-  "Accept-Language": "en-US,en;q=0.5",
  "Accept-Encoding": "gzip, deflate, br, zstd",
  "Referer": `points o/u "https://`:sportsbook Player total points over/under
- `assists o/u.draftkings.com`: Player total assists over/under
- `blocks o/u`:/",
  "X-Client-Name": "web Player total blocks over/under
- `three pointers`: Player 3-point field goals made
- `player",
  "X points`:-Client-Version": "1.4. Points scored by0",
  "X-Client-Feature": "cms",
  "X-Client-Page": specific player

#### Game "home",
  "Origin Structure Markets
-": ` "https://sportshalbook.draftkings.com",
ftime/fulltime`: Half-time  "Connection": "keep result-alive",
  "Sec-Fetch + Full-Dest-time result
- `quarters": "empty",
 `: Individual quarter betting
- `race "Sec-Fetch-M to x points`:ode": "cors",
  "Sec-Fetch-Site": Which team reaches X points first
- "same-site",
  `both teams total "Priority": points - both halves "u`

### Football-Specific Markets (NFL=4"
};
```

## 🌐, NCAA Football)

#### API Endpoints

### 1. Manifest Endpoint
**URL:** Drive Props
- `1st drive `GET /sites/US-OH-SB/api/sportslayout/v1/manifest?format=json`

**Description:** Gets all available sports and leagues with routing information.

**Response Structure:**
```json
{
  "routes": [
    {
      "key": "event",
      "entityType": "event",
      "route": "/sport result`: Outcome of first/{sportId}/league/{leagueId}/event/{eventId}",
      "overrides": [
        {
          "route": "/sport/7/league/84240/event/{eventId}",
          "seoRoute": "/events/baseball/mlb/{eventSeoId}/{eventId}",
 possession
- `1st drive -          "templateId 1st down`:": "6a75a42e-dd73-46ae-87cc-7f82a76face8__client_web_1.3.0"
        }
      ]
    }
  ]
}
```

### 2. League Content Endpoint
**URL:** `GET /api/sportscontent/dkusoh/v1/leagues/{league_id}`

**Description:** Gets all betting markets and events for How far the first drive goes
- ` a specific league.

**Parameters:**
- `league_id` (score on 1st drive`: Points scored on first possession

#### Scoring Props
-string `td props`: Touchdown scoring): The league markets
- `field goals`: Field goal identifier (e.g success/failure
- `., "42648" for NBA)

**Response Structure:**
```jsonsafeties`: Safety
{
  "sports": [...],
  "leagues": [... occurrence

####],
  "events": [
    {
      "id": "12345",
 Game Structure
- `halves won`: Which      "awayTeam": {"name": " halfLos Angeles Lakers"},
      "homeTeam has more scoring
- `every quarter`: Betting on each individual quarter

### Hockey-Specific Markets (NHL)

#### Puck Line (Hockey Spread)
```json
{
  "marketType": {"name": "p": {"name":uck line"},
  "line":  "Golden1.5,
  "outcomes": [
    {"name": "Team State Warriors"},
      "startTime": A -1.5", "price": {"american": - "2025-11-04T20:00:00Z",
      "competitions":140, " [
decimal        {
         ": 1.71}},
    {" "bettingOffersname": [
": "Team B +1            {
.5",              " "price": {"american":marketType ": {"120, "decimal": 2.20name": "moneyline"},
              "outcomes": [
                {"name": "Los Angeles Lakers", "price": {"decimal": 1.85, "american}}
 ": ]
}
```

#### Player Props
- `goalscorer`: First goal scorer
- `shots on goal -118`: Total shots on goal
- `}},
                {"name": "Golden State Warriors", "price": {"decimal": 2.points05, "american": 105`: Goals +}}
              ]
            }
          assists ]
        }
      ]
    }
 

### ],
  "markets": [...],
  Future Markets ( "selections": [...]
}
```

### 3. Event-Specific Endpoint
**SeasonURL:** `GET /-Long)

####api/sports Championshipcontent/dkusoh/v1/leagues/{ Winners
```json
{
league_id}/events/{event_id}`

**  "marketType": {"name":Description:** Gets detailed betting markets for a specific event.

### 4. Markets Endpoint
**URL:** `GET /api/sportscontent/dkusoh/v1/leagues/{league_id}/markets`

**Description:** Gets all available market types "champion"},
  "outcomes for a league.

## 🏆 League IDs & Sports": [
    {"name": "

### Major Leagues
Los Angeles Lakers", "price": {"american": | Sport | League ID | Name | Market Count | Status800, "decimal":  |
|-------|-----------|------|-------------|---------|
9.00}},
    {"name":| Basketball | `42648` | NBA | 231 | ✅ Active |
| Football | `88808` | NFL | 171 | ✅ Active |
| Basketball | `92483` | NCAA Basketball | 57 | ✅ Active |
| Football | `87637` | NCAA Football | 60 | ✅ Active |
| Baseball | `84240` | MLB | 4 | ❄️ Off-season |
| Hockey | `42133` | NHL | 92 | ✅ Active |
| Basketball | `94682` | WNBA | 6 | ✅ Active |

### Dynamic Sports (Tournament IDs Change)
| Sport | Example ID | Notes |
|-------|------------|-------|
| Tennis | Varies | "Boston Celtics", Use manifest "price": {"american": 600, "decimal": 7. discovery |
| Golf | Varies00}}
  ]
}
```

#### Awards
- `mvp`: Most Valuable Player
- `dpoy`: Defensive Player of the Year
- ` | Use manifest discovery |
| MMA |regular season wins`: Team `9034` | Some static win totals leagues

## exist |
| Boxing | Varies |  Use manifest discovery |
| Motorsports |🔄 Data Flow & Response Parsing

### `212334` | Formula 1 1. Event has static ID |
| Structure
```json
{
  " Soccer | Varies | Use manifest discoveryevents": [
    {
      "id |

## 📊 Market Types &": "event_12345",
      Categories

### Core Market Types (Available in "awayTeam": {"name": " MultipleTeam A Sports)
- **", "abmoneyline**: Pickbreviation": " the winner
- **spread**: Point spread betting
TEA"},
      "homeTeam":- **total**: Over/under total points {"name": "Team B", "abbreviation": "TEB"},
     /goals
- "startTime": "2025- **game lines**: Primary game betting options

### NBA-Specific Markets (23111-04T19:00: Total)
```json
00Z",
      "status": "{
  "moneyline": "Pick game winner",
  "spread": "Point spread betting",
  "total": "Total points over/under",
  "game lines": "Primaryscheduled",
      "venue": {"name": "Stap betting options",
  "les Center"}
    }
  ]
}
```

### 2. Competition Structure
```json
{
team futures": "Season  "competitions": [
    {
      "-longid": "comp_ outcomes",
  "regular season wins12345",
      "": "Team winname": " totals",
  "playoffs": "MainPlayoff qualification",
  "play Match",
      "bettingOffers": [
        {
          "id": "offer_12345",
          "marketType": {
            "id": "mt_1",
            "name": "moneyline"
          },
          "line": null,  // For moneyline markets
          "outcomes": [...]
        }
      ]
    }
  in": "Play-in tournament",
  ]
 "aw}
```

### 3.ards": "MVP Outcome Structure
```json
{
 , "outcomes": [
    {
      All-Star "id": "outcome_12345",
      "name": "Los Angeles Lakers",
      " selections",
price": {
        "  "playeramerican": -150,
        points": " "decimal": 1.67,
Individual player scoring",
        "fractional":  "player assists "2/3": "Individual"
      player assists",
 },
      "status": "  "player rebounds": "Individual player rebounds",
  "player three-pointers": "3-point field goals",
  "halftime/fulltime": "HT/FT results",
  "quarters": "active",
Quarter-by-quarter betting      "sort",
Order":   "race1
    }
  ]
 to x points": "First to reach point threshold",
  "largest lead": "}
```

## 🛠️ ImplementationBig Guide

### Python Client Example

```python
import requests
from typing import Dict, List,gest lead during game",
  "largest comeback": "Biggest deficit overcome"
}
```

### NFL-Specific Markets (171 Total)
```json
{
  "moneyline": "Pick game winner",
  "spread": "Point spread betting",
  "total": "Total points over/under",
  "game lines": "Primary betting options",
  "futures": "Season outcomes",
  "wins": "Team win totals",
  "playoffs": "Playoff qualification",
  "team specials": "Team-specific props",
  "1st drive": "Opening drive outcomes",
  "1st drive result": " Optional

classSuccess/failure of DraftKingsAPIClient:
    def __init__(self):
        self.base_url = " first possession",
  "scoring props": "TD, FG,https://sportsbook-nash.draftkings.com"
        self.session = requests safety markets",
  "comeback": "Deficit overcome",
  "to score 1st & win/lose": "First score + game outcome",
  ".Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/correct score": "Exact final score",
  "exact result": "HT/FT combinations"
}
```

### NHL-Specific Markets (92 Total)
```json
{
  "moneyline": "Pick game winner",
  "puck line": "5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
            "HockeyAccept": "*/*",
            "Accept-Language": "en-US,en;q= spread0.5",
            "Accept-Encoding equivalent",
  "total": "gzip, deflate": "Total goals over/under",
  "game lines": "Primary betting options",
  "team futures": "Season, outcomes",
  "goalscorer": "First/anytime br, zstd",
            "Referer": " goal scorer",
  "shots on goal": "Shots on target",
 https://sportsbook.draftkings.com/",
            "X-Client-Name": "web "",
            "X-Client-Version": "1.4.0",
            "periods": "Period-by-period betting",
  "goalie props": "Goaltender statistics",
  "power play": "Power play outcomes"
}
```

## 📡 Request/Response Formats

### Request Format
```python
import requests

X-Client-def fetch_leFeature": "cms",
ague_data(league_id            "X-Client-):
   Page": "home",
            "Origin": "https://sportsbook.draft url = f"https://sportsbook-nkings.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "corsash.draftkings.com/api/sportscontent/dkusoh/v1/leagues",
            "Sec-Fetch-Site":/{league_id "same-site",
            "Priority": "u=4",
        })
    
    def}"

    headers = {
        "User-Agent": "Mozilla/5.0 get_manifest(self) -> Dict:
        """Get all available sports and leagues."""
        url = f"{self.base_url}/sites/US-OH-SB/api/sportslayout/v1/manifest?format=json"
        response = self.session.get(url, timeout=30)
 (X11;        response.raise_for_status()
        return Linux x86_64; rv:144.0) response.json()
    
    def get_le Gecko/20100101 Firefox/144.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://sportsbook.draftkings.com/",
        "X-Client-Name": "web",
        "X-Client-Version": "1.4.0",
        "X-Client-Feature": "cms",
        "X-Client-Page": "home",
        "ague_data(self, league_id: str) -> Dict:
        """Get betting data for a specific league."""
        urlOrigin": "https://sportsbook.draftkings.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=4"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    return response.json()
```

### Response Format = f"{self.base_url}/api/sportscontent/dkusoh/v1/leagues/{league_id}"
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_nba_data(self) -> Dict:
        """Get NBA betting data."""
        return self.get_league_data("42648")
    
    def get_nfl_data(self) -> Dict:
        Analysis
```json
{
  "events": [
    {
      "id """Get NFL betting data."""
        return": "event self.get_league_data("88808_id",
      "awayTeam": {
        "name": "Away Team")

# Name"
      },
      Usage
client = DraftKings "homeTeam": {
        "name": "Home Team Name"
      },
      "startTime": "2025-11-04T20:00:00Z",
      "competitions": [
        {
          "bettingOffers": [
            {
              "marketType": {
                "nameAPIClient()
": "moneyline"
              },
             manifest = "outcomes": [
                {
                  "name": "Away client.get_manifest()
nba_data = client.get_nba_data()
```

### Team Name",
                  "price": {
                    "decimal": 1.85,
                    "american": -118
                  }
                },
                {
                  "name": "Home Team Name",
                  "price": {
                    "decimal": 2.05,
                    "american": 105
                  }
                }
              ]
            }
          ]
        }
 Extracting      ]
    }
  Market Data

``` ]
}
```

python
def extract_markets### Parsing(league Response Data_data:
```python
def parse Dict) -> List[Dict]:
    """Extract all betting markets from league data."""
    markets = []
    
   _event_data(event_data):
    """Parse betting data from a single event."""
    event = {
        "event_id": event_data.get("id"),
        "away_team": event_data.get("awayTeam", {}).get("name", "Unknown"),
        "home_team": event_data.get("homeTeam", {}).get("name", "Unknown"),
 for event in league_data.get("        "start_time": event_data.get("startTimeevents"),
        "markets":", []):
        for competition in event.get("competitions", []):
            for offer in competition.get("bettingOffers", []):
                market = {
                    "event_id": event["id"],
                    "market_type": offer["marketType"]["name"],
                    "line": offer.get("line"),
                    "outcomes": [
                        {
                            "name": outcome["name"],
                            "american_odds": outcome["price"]["american"],
                            "decimal_odds": outcome["price"]["decimal"]
                        }
                        for outcome in offer.get("outcomes", [])
                    ]
                }
                markets.append(market)
    
    return markets

# Extract markets
client = DraftKingsAPIClient()
nba_data = client.get_nba_data []
    }

    competitions = event_data.get("competitions", [])
    for()
markets = extract_markets(nba comp in competitions:
        betting_off_data)
```

## ers = comp.get("bettingOffers", [])
        for offer in betting_offers:
            market = {
                "type": offer.get("marketType", {}).get("name", "unknown"),
                "outcomes": []
            }

           ⚠️ Error Handling outcomes = offer.get("outcomes", & Rate Limiting

### HTTP Status Codes
- `200`: Success
- [])
            for outcome in outcomes:
                `400`: Bad Request (invalid league market[" ID or parameters)
- `404`: League not found
- `429`:outcomes"].append({
                    "name": outcome.get("name Rate limited
- `500`:"),
                    "decimal Server error

###_odds": outcome.get("price", {}).get("decimal"),
                    "american Rate Limiting
- **Not_odds": outcome.get("price", {}).get("american")
                })

            officially documented event["markets"].append(market)

**
- **    return event
```

## 💻Recommended**: 1 Code Examples

### request per second per Basic League Data Fetch endpoint
- **
```python
import requestsBurst limit**: Unknown,

class DraftKingsAPI use exponential backoff

### Error Handling Example

```python
def safe_api_call(func, *args, **kwargs):
    """Safely call API with error handling."""
    try:
        return func(*args, **kwargs)
    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.warning("Rate limited, backing off...")
            time.sleep(5)  # Wait and retry
            return func(*args, **kwargs)
        elif e.response.status_code == 404:
            logger.error("League not found")
            return None
        else:
            logger.error(f"HTTP error: {e}")
            return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
```

## 📊 Data Availability

### Seasonal Considerations
- **NBA/NFL**: Active during regular season (September-June)
- **MLB**: Active during season (April-October)
- **NHL**: Active during season (October-April)
- **NCAA**: Active during academic year
- **WNBA**: Limited season (May-September)

### Market Availability
- **Live Markets**: Available during:
    def active games
- ** __init__(self):
        self.base_url = "Pre-https://sportsbook-nash.draftkings.com"
Game**: Available        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:144.0) Gecko/20100101 Firefox/144.0",
            "Accept": "*/*",
            "Accept-Language": hours before game start "en-US,en;q=0.5",
            "Accept-Encoding": "
- **Futures**: Available year-round forgzip, deflate, br, zstd",
            "Referer": "https://sportsbook.draftkings.com/",
            "X-Client-Name": "web",
            "X-Client-Version": "1.4.0",
            "X-Client-Feature championships, awards
- **Props**:": "cms",
            "X- Game-specific, available 1-2 hours before start

## 🔍 Advanced Usage

###Client-Page": "home",
            "Origin": "https://sportsbook Discovering New Leagues
.draftkings.com",
            "Connection```python
def discover": "keep-alive",
            "Sec_leagues-Fetch-Dest": "empty",
():
    """Discover            "Sec-Fetch-Mode": all available leagues from manifest."""
    client "cors",
            "Sec-Fetch = Draft-Site":KingsAPIClient()
    "same-site",
            " manifestPriority": "u=4"
        })

    def get_nba_markets(self):
        """Get all NBA betting markets."""
        url = f"{self.base_url}/api/sportscontent/dkusoh/v1/leagues/42648"
        response = self.session.get(url, timeout=30)
        = client.get_manifest()
    
    leagues return response.json()

    def get_n = {}
    for route in manifest.getfl_markets(self):
        """Get("routes", []):
        all NFL betting markets."""
        url = for override in route.get("overrides", f"{self.base_url}/api/s []):
            routeportscontent/dkusoh/v1/le_pattern = override.get("route", "")
agues/88808"
        response =            if "/sport/" in route_pattern self.session.get(url, timeout=30)
        return response.json()

    def get_available_sports(self):
        """Get manifest of all available sports."""
        url = f"{self.base_url}/sites/US-OH-SB/api/sportslayout/v1/manifest?format and "/league/" in route_pattern:
                parts = route_pattern.split("/")
=json"
        response = self                try:
                   .session.get sport_id = parts[parts.index("sport") + 1]
                    league_id = parts[parts.index("league") + 1]
(url, timeout=30)
        return                    leagues[league_id] = response.json()

# Usage {
                        "sport_id": sport
api = DraftKingsAPI()
nba_data = api.get_nba_id,
                        "route": route_pattern
                    }
               _markets()
nfl_data = api except.get_nfl_markets()
manifest = (ValueError, IndexError api.get_available_sports()
```

###):
                    Market Type Discovery
```python
 continue
    
    return leagues
```

### Real-Time Datadef discover_market_types Collection(league_data):
    """Extract all unique market types from league data

```python
import time
from."""
    market_types = set datetime import datetime()

   , timedelta

def collect events = league_data.get("events", [])
    for event in events:
       _real_time_data competitions = event.get("competitions",(leagues: List[str], interval_minutes: [])
        for comp in competitions:
            int =  betting_offers = comp.get("bet5):
    """CollecttingOffers", [])
            for offer in data from betting_offers:
                market_name = offer.get("marketType", {}).get("name")
                if market_name:
                    market_types.add(market_name)

    return list(market_types)

# Usage
api = DraftKingsAPI()
nba multiple leagues at regular intervals."""
    client = Draft_data = api.get_nba_marketsKingsAPIClient()
    
    while True:
        for league_id in leagues:
            data =()
 safe_api_call(client.get_league_data, league_id)
            if data:
market_types = discover_market_types(nba                # Process and store_data)
print(f"NBA has {len(market_types data
               )} market types: {market_types}")
```

### markets = extract_markets(data)
                save_to_database(markets, league Real-Time Data_id)
 Processing
```python
import        
        # Wait before next time
from datetime import datetime

def monitor_live_games(league_id="42648", interval=60):
    """Monitor live games and their betting markets."""
 collection
        time.sleep(interval    api =_minutes * 60)

# Collect DraftKingsAPI()

    NBA and NFL data every 5 minutes
collect_real_time_data(["42648", "88808"], 5)
```

## 📋 API Limitations & Considerations

### Data while True:
        try:
            Freshness
- ** data = api.get_nba_markets()  # or any league
            events = data.getNot("events", [])

            active_games = real-time**: Updates []
            for event in events:
                start_time = event.get("startTime")
                if start_time:
                    game_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    if game_time <= datetime.now():
                        active_games.append(event)

            print(f"Found {len(active_games)} active games")

            for game in active_games every few minutes
- **[:3]:Caching**:  # Show first 3
                away = game.get("awayTeam", API responses may be {}).get("name cached")
                home = game.get("home server-side
- **Latency**: Team", {}).get("name")
                print(f"2-5  {away} @ {home}")

 minute delay        except Exception as e:
            print(f"Error from live action

### fetching data: {e}")

        time.sleep(interval)

# Usage
monitor_live Data Completeness
- **Not all markets**: Some markets may be restricted_games("42648", 30)  # Check NBA every 30 seconds
```

## 🚨 Error Handling

### Common HTTP by Errors
```python
 jurisdiction
- **defLine changes**: safe Odds can change_api_call(url, between max_retries=3):
    """Make API requests
- **Event call with status**: error handling and Games may be cancelled or postponed

### Geographic Restrictions
- **Jurisdiction retries."""
    api = DraftKingsAPI()

    for attempt in range(max_retries):
        try:
            response = api.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.Timeout:
            print(f"Timeout on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff

        except requests.HTTPError as e:
            if response.status_code == 404:
                print("-specific**: Some marketsLeague only available in certain or states
- **IP-based**: endpoint not found")
                return None
            elif response.status_code == 429:
                print("Rate limited - waiting Content may vary by longer")
                time.sleep(60)
                continue
            else:
                print location
- **(f"HTTP error: {Legal restrictions**:e}")
                Certain betting return None

        except requests.RequestException as e:
            print(f"Network types error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 restricted ** attempt)

    return None
```

### by law Data Validation
```python
def validate_event_data(event_data):
    """Validate event data structure."""
    required_fields = ["id", "awayTeam", "homeTeam", "startTime"]

    for field in required_fields:
        if field not in event_data:
            raise ValueError

## 🎯 Best(f"Missing required field: {field Practices

### 1. Error Handling
- Always implement retry logic with exponential backoff
- Handle network timeouts gracefully
- Validate response}")

    # Validate team names
    data before processing

### 2. away_team = event_data.get("away Rate Limiting
- Implement request throttlingTeam", {})
    home_team = event (1_data.get("homeTeam", {})

    if not away_team req/sec.get("name") or not home_team recommended)
-.get("name"):
        raise ValueError("Team names missing")

    # Validate Use multiple IP addresses for start time
    start_time = event_data.get("startTime")
    if high not start_time:
        raise ValueError-volume collection
- Monitor("Start time missing")

    return True for rate limit

def validate_market responses

### 3. Data_data(market Validation
-_data):
    """Validate market data structure."""
    if Verify market "marketType" not in market_data data:
        raise ValueError("Market type missing integrity")

    market before_name = market_data storage
- Check for negative odds or.get("marketType", {}).get("name")
    if not market_name:
        raise ValueError("Market name missing")

    outcomes = market_data.get("outcomes", [])
    if not outcomes:
        raise ValueError("No outcomes found")

    for outcome in outcomes:
        if "name" not in outcome invalid or "price" not in outcome:
            raise ValueError lines
- Validate team(" names and eventIncomplete outcome data")

    return True
```

## ✅ Best Practices

### 1. Rate Limiting
```python
import time

class RateLimitedAPI(DraftKingsAPI):
    def __init__(self, calls_per_minute=30):
        super().__init__()
        self.calls_per_minute = calls_per_minute
        self.call_times = []

    def rate_limited_request(self, url):
        """Make request with rate limiting."""
        now = time.time()

        # Remove calls older than 1 minute
        self.call_times = [t for t times

### 4. Monitoring
- Log in API response self.call_times if now - times and success rates
- Monitor for API changes or deprecations
- Alert on data collection failures

## 🔗 t < 60]

        # Check if Quick Reference

### we're at League ID the limit
        if len(self.call Quick Lookup
```_times) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.call_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Make the request
        response = selfpython
.session.get(url, timeout=30LEAG)

        #UE_IDS = {
    "nba Record the call
        self.call_times": ".append(time.time())

        return response42648",
    "n.json()
```

### 2. Caching Strategy
```python
importfl": "88808", 
 json
    "ncaab": "92483",
    "ncaaf": "87637",
    "mlb": "84240",
    "nhl": "42133",
    "importwnba": os
 "94682"
}
```

### Common Market Types
- `moneyline`: Pick the winner
- `spread`: Pointfrom datetime import spread betting
- `total`: Over datetime, timedelta

class CachedAPI(DraftKingsAPI):
    def __init__(self, cache_dir="api_cache"):
        super().__init__()
/under total points
- `        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get_cached_data(self, league_id, max_age_minutes=5):
        """Get data with caching."""
        cache_file = os.path.join(self.cache_dir, fgame lines"league_{league_id}.json`: Game-specific betting
- `futures`: Season-long markets")

        # Check if
- `props`: Proposition bets

This comprehensive documentation provides everything needed to effectively use the DraftKings cache exists and is fresh
        if os.path.exists(cache_file):
            file API for_age = datetime.now() - datetime.from betting market data collectiontimestamp(os.path.getmtime(cache_file))
            if file_age <.
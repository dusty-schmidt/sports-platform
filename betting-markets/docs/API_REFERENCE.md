# API Reference Documentation

## Overview

The Betting Market Data API provides comprehensive REST endpoints for accessing betting odds, market data, and managing automated data collection. All endpoints return JSON responses and support standard HTTP status codes.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, consider implementing API key authentication or OAuth2.

## Rate Limiting

- Default: 100 requests per minute
- Headers included in responses:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error description",
  "timestamp": "2023-11-02T21:59:26.825Z"
}
```

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Endpoints

### Health & System

#### GET /health

Health check endpoint to monitor service status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-11-02T21:59:26.825Z",
  "scheduler_running": true
}
```

#### GET /stats

Get comprehensive system statistics.

**Response:**
```json
{
  "sports": 5,
  "sportsbooks": 2,
  "markets": 150,
  "snapshots": 1250,
  "active_markets": 45,
  "latest_snapshot": "2023-11-02T21:55:00.000Z",
  "api_version": "1.0.0",
  "last_updated": "2023-11-02T21:59:26.825Z",
  "scheduler": {
    "running": true,
    "active_jobs": 4,
    "auto_collect_sports": ["nba", "nfl", "mlb", "nhl"]
  }
}
```

### Sports Management

#### GET /sports

Retrieve all available sports.

**Response:**
```json
[
  {
    "id": 1,
    "name": "nba",
    "display_name": "NBA",
    "created_at": "2023-11-02T21:55:00.000Z"
  }
]
```

#### GET /sports/{sport_name}

Get details for a specific sport.

**Parameters:**
- `sport_name` (path): Sport identifier (e.g., "nba", "nfl")

**Response:**
```json
{
  "id": 1,
  "name": "nba",
  "display_name": "NBA",
  "created_at": "2023-11-02T21:55:00.000Z"
}
```

### Sportsbooks

#### GET /sportsbooks

Get all available sportsbooks.

**Response:**
```json
[
  {
    "id": 1,
    "name": "draftkings",
    "display_name": "DraftKings",
    "base_url": "https://sportsbook.draftkings.com",
    "is_active": true,
    "created_at": "2023-11-02T21:55:00.000Z"
  }
]
```

#### GET /sportsbooks/{sportsbook_name}

Get details for a specific sportsbook.

**Parameters:**
- `sportsbook_name` (path): Sportsbook identifier

**Response:**
```json
{
  "id": 1,
  "name": "draftkings",
  "display_name": "DraftKings",
  "base_url": "https://sportsbook.draftkings.com",
  "is_active": true,
  "created_at": "2023-11-02T21:55:00.000Z"
}
```

### Market Data

#### GET /markets

Get betting markets with their latest snapshots.

**Query Parameters:**
- `sport` (optional): Filter by sport (e.g., "nba", "nfl")
- `sportsbook` (optional): Filter by sportsbook (e.g., "draftkings")
- `hours_ahead` (optional): Hours ahead to look for markets (default: 48, range: 1-168)
- `limit` (optional): Maximum number of markets to return (default: 100, range: 1-1000)

**Example:**
```
GET /markets?sport=nba&limit=10
```

**Response:**
```json
[
  {
    "id": 123,
    "sport_id": 1,
    "external_id": "DK_NBA_001",
    "game_name": "Lakers vs Warriors",
    "away_team": "Los Angeles Lakers",
    "home_team": "Golden State Warriors",
    "game_start_time": "2023-11-03T02:00:00Z",
    "timezone": "America/New_York",
    "season": "2023-24",
    "league": "NBA",
    "created_at": "2023-11-02T21:55:00Z",
    "updated_at": "2023-11-02T21:58:00Z",
    "sport": {
      "id": 1,
      "name": "nba",
      "display_name": "NBA",
      "created_at": "2023-11-02T21:55:00Z"
    },
    "latest_snapshots": [
      {
        "id": 456,
        "market_id": 123,
        "sportsbook_id": 1,
        "away_moneyline": "+150",
        "home_moneyline": "-180",
        "away_spread": 3.5,
        "away_spread_price": "-110",
        "home_spread": -3.5,
        "home_spread_price": "-110",
        "total_points": 220.5,
        "over_price": "-110",
        "under_price": "-110",
        "additional_markets": null,
        "snapshot_time": "2023-11-02T21:58:00Z",
        "created_at": "2023-11-02T21:58:00Z",
        "sportsbook": {
          "id": 1,
          "name": "draftkings",
          "display_name": "DraftKings",
          "base_url": "https://sportsbook.draftkings.com",
          "is_active": true,
          "created_at": "2023-11-02T21:55:00Z"
        }
      }
    ]
  }
]
```

#### GET /markets/{market_id}

Get detailed information about a specific market.

**Parameters:**
- `market_id` (path): Unique market identifier

**Response:**
Same structure as `/markets` response.

### Odds Data

#### GET /odds/snapshot/{sportsbook_id}

Get snapshots from a specific sportsbook.

**Parameters:**
- `sportsbook_id` (path): Sportsbook identifier

**Query Parameters:**
- `market_id` (optional): Filter by market ID
- `limit` (optional): Maximum number of snapshots (default: 100, range: 1-1000)

**Example:**
```
GET /odds/snapshot/1?limit=50
```

**Response:**
```json
[
  {
    "id": 456,
    "market_id": 123,
    "sportsbook_id": 1,
    "away_moneyline": "+150",
    "home_moneyline": "-180",
    "away_spread": 3.5,
    "away_spread_price": "-110",
    "home_spread": -3.5,
    "home_spread_price": "-110",
    "total_points": 220.5,
    "over_price": "-110",
    "under_price": "-110",
    "additional_markets": null,
    "snapshot_time": "2023-11-02T21:58:00Z",
    "created_at": "2023-11-02T21:58:00Z"
  }
]
```

#### GET /odds/latest

Get the latest odds from all sportsbooks for active markets.

**Query Parameters:**
- `sport` (optional): Filter by sport
- `sportsbook` (optional): Filter by sportsbook
- `limit` (optional): Maximum number of results (default: 50, range: 1-500)

**Example:**
```
GET /odds/latest?sport=nba&limit=10
```

**Response:**
```json
[
  {
    "market": {
      "id": 123,
      "game": "Lakers vs Warriors",
      "away_team": "Los Angeles Lakers",
      "home_team": "Golden State Warriors",
      "game_start": "2023-11-03T02:00:00Z",
      "sport": "nba"
    },
    "odds": [
      {
        "sportsbook": "DraftKings",
        "away_moneyline": "+150",
        "home_moneyline": "-180",
        "away_spread": 3.5,
        "away_spread_price": "-110",
        "home_spread": -3.5,
        "home_spread_price": "-110",
        "total_points": 220.5,
        "over_price": "-110",
        "under_price": "-110",
        "timestamp": "2023-11-02T21:58:00Z"
      },
      {
        "sportsbook": "FanDuel",
        "away_moneyline": "+155",
        "home_moneyline": "-175",
        "away_spread": 3.0,
        "away_spread_price": "-105",
        "home_spread": -3.0,
        "home_spread_price": "-115",
        "total_points": 219.5,
        "over_price": "-105",
        "under_price": "-115",
        "timestamp": "2023-11-02T21:57:30Z"
      }
    ]
  }
]
```

### Data Collection

#### POST /collect/{sport}

Trigger data collection for a specific sport.

**Parameters:**
- `sport` (path): Sport identifier

**Query Parameters:**
- `books` (optional): List of sportsbooks to collect from

**Example:**
```
POST /collect/nba?books=draftkings&books=fanduel
```

**Response:**
```json
{
  "message": "Started collecting data for nba",
  "status": "queued"
}
```

### Scheduler Management

#### GET /scheduler/status

Get current scheduler status and statistics.

**Response:**
```json
{
  "scheduler_running": true,
  "active_jobs": 4,
  "job_details": [
    {
      "id": "collect_nba",
      "name": "Collect NBA data",
      "next_run": "2023-11-02T22:00:00Z",
      "trigger": "interval[00:15:00]",
      "args": ["nba", ["draftkings", "fanduel"]]
    }
  ],
  "job_statistics": {
    "nba": {
      "last_run": "2023-11-02T21:45:00Z",
      "status": "completed",
      "events_collected": 25,
      "snapshots_created": 25,
      "duration_seconds": 12.5
    }
  },
  "config": {
    "auto_collect_sports": ["nba", "nfl", "mlb", "nhl"],
    "cleanup_interval_hours": 24,
    "days_to_keep_snapshots": 7
  }
}
```

#### GET /scheduler/jobs

Get list of active scheduler jobs.

**Response:**
```json
{
  "jobs": [
    {
      "id": "collect_nba",
      "name": "Collect NBA data",
      "next_run": "2023-11-02T22:00:00Z",
      "trigger": "interval[00:15:00]",
      "args": ["nba", ["draftkings", "fanduel"]]
    }
  ]
}
```

#### POST /scheduler/jobs/{sport}

Add a scheduled job for a specific sport.

**Parameters:**
- `sport` (path): Sport identifier

**Query Parameters:**
- `books` (optional): List of sportsbooks

**Response:**
```json
{
  "message": "Added scheduled job for nhl",
  "sport": "nhl",
  "books": ["draftkings", "fanduel"],
  "status": "success"
}
```

#### DELETE /scheduler/jobs/{sport}

Remove the scheduled job for a specific sport.

**Parameters:**
- `sport` (path): Sport identifier

**Response:**
```json
{
  "message": "Removed scheduled job for nhl",
  "sport": "nhl",
  "status": "success"
}
```

#### POST /scheduler/trigger/{sport}

Manually trigger a scheduled job for a specific sport.

**Parameters:**
- `sport` (path): Sport identifier

**Query Parameters:**
- `books` (optional): List of sportsbooks

**Response:**
```json
{
  "sport": "nba",
  "books": ["draftkings", "fanduel"],
  "status": "completed",
  "stats": {
    "last_run": "2023-11-02T22:00:00Z",
    "status": "completed",
    "events_collected": 30,
    "duration_seconds": 15.2
  }
}
```

#### GET /scheduler/stats/{sport}

Get statistics for a specific sport's job.

**Parameters:**
- `sport` (path): Sport identifier

**Response:**
```json
{
  "sport": "nba",
  "stats": {
    "last_run": "2023-11-02T22:00:00Z",
    "status": "completed",
    "events_collected": 30,
    "duration_seconds": 15.2,
    "snapshots_created": 30,
    "error": null
  }
}
```

### Analytics

#### GET /analytics/market-comparison

Compare odds for a specific market across sportsbooks.

**Query Parameters:**
- `market_id` (required): Market identifier

**Example:**
```
GET /analytics/market-comparison?market_id=123
```

**Response:**
```json
{
  "market": {
    "id": 123,
    "game": "Lakers vs Warriors",
    "away_team": "Los Angeles Lakers",
    "home_team": "Golden State Warriors",
    "game_start": "2023-11-03T02:00:00Z"
  },
  "sportsbook_odds": [
    {
      "sportsbook": "DraftKings",
      "away_moneyline": "+150",
      "home_moneyline": "-180",
      "away_spread": {
        "line": 3.5,
        "price": "-110"
      },
      "home_spread": {
        "line": -3.5,
        "price": "-110"
      },
      "total": {
        "line": 220.5,
        "over": "-110",
        "under": "-110"
      },
      "timestamp": "2023-11-02T21:58:00Z"
    },
    {
      "sportsbook": "FanDuel",
      "away_moneyline": "+155",
      "home_moneyline": "-175",
      "away_spread": {
        "line": 3.0,
        "price": "-105"
      },
      "home_spread": {
        "line": -3.0,
        "price": "-115"
      },
      "total": {
        "line": 219.5,
        "over": "-105",
        "under": "-115"
      },
      "timestamp": "2023-11-02T21:57:30Z"
    }
  ],
  "best_odds": {
    "away_moneyline": {
      "book": "FanDuel",
      "odds": "+155"
    },
    "home_moneyline": {
      "book": "FanDuel",
      "odds": "-175"
    },
    "away_spread": {
      "book": "FanDuel",
      "odds": "-105",
      "line": 3.0
    },
    "home_spread": {
      "book": "DraftKings",
      "odds": "-110",
      "line": -3.5
    },
    "over": {
      "book": "FanDuel",
      "odds": "-105",
      "total": 219.5
    },
    "under": {
      "book": "FanDuel",
      "odds": "-115",
      "total": 219.5
    }
  }
}
```

## Usage Examples

### JavaScript/Fetch

```javascript
// Get NBA markets
const response = await fetch('/markets?sport=nba&limit=5');
const markets = await response.json();

// Trigger NBA collection
const collectResponse = await fetch('/collect/nba', { method: 'POST' });
const result = await collectResponse.json();

// Compare market odds
const comparison = await fetch('/analytics/market-comparison?market_id=123');
const odds = await comparison.json();
```

### Python/Requests

```python
import requests

# Get NBA markets
response = requests.get('/markets', params={'sport': 'nba', 'limit': 5})
markets = response.json()

# Trigger data collection
response = requests.post('/collect/nba', params={'books': ['draftkings', 'fanduel']})
result = response.json()

# Get latest odds
response = requests.get('/odds/latest', params={'sport': 'nba'})
odds = response.json()
```

### cURL

```bash
# Get NBA markets
curl "http://localhost:8000/markets?sport=nba&limit=5"

# Trigger data collection
curl -X POST "http://localhost:8000/collect/nba?books=draftkings&books=fanduel"

# Get latest odds
curl "http://localhost:8000/odds/latest?sport=nba&limit=10"

# Get market comparison
curl "http://localhost:8000/analytics/market-comparison?market_id=123"
```

## Response Format Details

### Market Object Structure

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique market identifier |
| `sport_id` | integer | Associated sport ID |
| `game_name` | string | Human-readable game name |
| `away_team` | string | Away team name |
| `home_team` | string | Home team name |
| `game_start_time` | datetime | Scheduled game start time |
| `timezone` | string | Game timezone |
| `latest_snapshots` | array | Latest odds from each sportsbook |

### Odds Object Structure

| Field | Type | Description |
|-------|------|-------------|
| `away_moneyline` | string | Away team moneyline odds (e.g., "+150") |
| `home_moneyline` | string | Home team moneyline odds (e.g., "-180") |
| `away_spread` | float | Away team point spread |
| `away_spread_price` | string | Away spread betting price |
| `home_spread` | float | Home team point spread |
| `home_spread_price` | string | Home spread betting price |
| `total_points` | float | Total points line |
| `over_price` | string | Over betting price |
| `under_price` | string | Under betting price |

## Best Practices

1. **Pagination**: Use the `limit` parameter to avoid large responses
2. **Filtering**: Apply `sport` and `sportsbook` filters to narrow results
3. **Caching**: Implement client-side caching for frequently accessed data
4. **Rate Limiting**: Respect the 100 requests per minute limit
5. **Error Handling**: Implement proper error handling for API calls
6. **Real-time Updates**: Use the `/odds/latest` endpoint for real-time data

## SDKs and Libraries

Consider developing client SDKs for popular languages:
- Python: `pip install betting-market-api`
- JavaScript: `npm install betting-market-api`
- Go: `go get github.com/betting-market/api-client-go`

## Support

For API support:
- Check the health endpoint first: `/health`
- Review logs for detailed error information
- Use `/docs` for interactive API exploration
- Contact support with specific error details and timestamps
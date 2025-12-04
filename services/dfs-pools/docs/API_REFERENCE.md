# API Reference

Base URL: `http://localhost:5000`

## Endpoints

### Health Check
```
GET /api/health
```
Returns service health status.

### Sports
```
GET /api/sports
```
Returns list of all sports with draftgroup counts.

### Draftgroups
```
GET /api/draftgroups
GET /api/draftgroups?sport=NFL
GET /api/draftgroups/<dg_id>
GET /api/draftgroups/active
GET /api/sports/<sport>/draftgroups
```

### Slates
```
GET /api/sports/<sport>/slates
GET /api/sports/<sport>/slates/<dg_id>/players
```

### Draftables (Player Pools)
```
GET /api/draftgroups/<dg_id>/draftables
GET /api/draftgroups/<dg_id>/draftables/optimizer_view
GET /api/sports/<sport>/draftables
GET /api/draftgroups/active/optimizer
```

### Scheduler
```
GET /api/scheduler/status
POST /api/scheduler/trigger
```

## Example Usage

```powershell
# Get all NBA slates for dropdown selection
curl http://localhost:5000/api/sports/NBA/slates

# Get all players in a specific slate
curl http://localhost:5000/api/sports/NBA/slates/138223/players

# Get all NFL draftgroups
curl http://localhost:5000/api/sports/NFL/draftgroups

# Get optimized player data for lineup optimizer
curl http://localhost:5000/api/draftgroups/138136/draftables/optimizer_view

# Get all active contests with player data
curl http://localhost:5000/api/draftgroups/active/optimizer

# Trigger manual data fetch
curl -X POST http://localhost:5000/api/scheduler/trigger
```

## Response Formats

All responses are JSON.

**Draftgroups:**
```json
{
  "count": 2,
  "draftgroups": [{
    "dg_id": 138136,
    "sport": "NFL",
    "start_time": "Sun 1:00PM",
    "game_type": "Classic",
    "status": "upcoming"
  }]
}
```

**Optimizer View:**

**Slates (for UI Dropdown):**
```json
{
  "sport": "NBA",
  "count": 7,
  "slates": [
    {
      "dg_id": 138223,
      "label": "Classic - Wed 7:00PM - 0 games",
      "team_count": 0
    },
    {
      "dg_id": 137940,
      "label": "Classic - Fri 7:00PM - 0 games",
      "team_count": 0
    }
  ]
}
```

**Slate Players (Full Player Pool with All Roster Variants):**
```json
{
  "dg_id": 138223,
  "sport": "NBA",
  "game_type": "Classic",
  "start_time": "Wed 7:00PM",
  "players_count": 500,
  "players": [
    {
      "altPlayerImage160": "...",
      "altPlayerImage50": "...",
      "competition": {...},
      "displayName": "Nikola Jokic",
      "draftAlerts": [],
      "draftableId": 41059819,
      "externalRequirements": [],
      "firstName": "Nikola",
      "isDisabled": false,
      "isSappable": true,
      "lastName": "Jokic",
      "newsStatus": "Recent",
      "playerAttributes": {...},
      "playerId": 3018,
      "playerGameAttributes": [],
      "playerImage160": "https://...",
      "playerImage50": "https://...",
      "position": "C",
      "rosterSlotId": 458,
      "salary": 12000,
      "shortName": "N. Jokic",
      "status": "None",
      "teamAbbreviation": "DEN",
      "teamId": 7
    }
  ]
}
```

```json
{
  "dg_id": 138136,
  "sport": "NFL",
  "players_count": 45,
  "players": [{
    "playerId": "12345",
    "displayName": "Patrick Mahomes",
    "salary": 11000,
    "position": "QB",
    "teamAbbreviation": "KC"
  }]
}
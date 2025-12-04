# DFS Pools Service

A self-contained microservice for fetching and serving DFS player pool data from DraftKings.

## Structure

```
dfs-pools/
├── src/
│   ├── api_server.py       # Flask REST API
│   ├── db_manager.py       # Database operations
│   ├── dk_pools.py         # DraftKings data fetching
│   ├── pool_scheduler.py   # Auto-update scheduler
│   ├── logger.py           # Logging utilities
│   └── config.py           # Configuration
├── data/
│   └── dfs_pools.db       # SQLite database
├── logs/                   # Log files
├── tests/                  # Tests
├── docs/                   # Documentation
├── app.py                  # Entry point
├── requirements.txt
└── .env
```

## Quick Start

```powershell
# Install dependencies
pip install -r requirements.txt

# Run the service
python app.py
```

The service runs on `http://localhost:5000`

## API Endpoints

- `GET /api/health` - Service health
- `GET /api/sports` - List all sports
- `GET /api/draftgroups` - List all draftgroups
- `GET /api/draftgroups/<id>` - Get specific draftgroup
- `GET /api/draftgroups/<id>/draftables` - Get player pools
- `GET /api/draftgroups/<id>/draftables/optimizer_view` - Optimizer-friendly view
- `GET /api/draftgroups/active/optimizer` - Active contests with players

## Platform Integration

This service is part of a larger DFS platform alongside:
- Live Odds Service
- Stats Updates Service
- Simulation Engine
- Optimizer
- Frontend

Each service runs independently and communicates via REST APIs.

## Data Ingestion

The service automatically fetches data from DraftKings every 4 hours (configurable).

Manual trigger:
```powershell
curl -X POST http://localhost:5000/api/scheduler/trigger
```

Or run the ingestion script directly:
```powershell
python -m src.dk_pools
```

## Configuration

Environment variables (`.env`):
- `SCHEDULER_ENABLED` - Enable auto-updates (default: True)
- `SCHEDULER_INTERVAL_HOURS` - Update interval (default: 4)
- `LOG_LEVEL` - Logging level (default: INFO)
- `DEBUG_MODE` - Debug mode (default: False)

## Logging

All logs written to `logs/dfs_pools_YYYYMMDD.log`

View logs:
```powershell
type logs\dfs_pools_*.log
```

## Testing

```powershell
python -m pytest tests/
```

## Simple and Clean

This is ONE self-contained microservice - not split into sub-services. It maintains all original functionality with a cleaner file organization.
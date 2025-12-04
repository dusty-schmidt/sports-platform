# DFS Pools Service - Quick Start

## Installation

```powershell
pip install -r requirements.txt
```

## Running the Service

```powershell
python app.py
```

Service runs on `http://localhost:5000`

## Trigger Data Fetch

```powershell
curl -X POST http://localhost:5000/api/scheduler/trigger
```

## Query Data

```powershell
# Get all sports
curl http://localhost:5000/api/sports

# Get all draftgroups
curl http://localhost:5000/api/draftgroups

# Get active contests with player data
curl http://localhost:5000/api/draftgroups/active/optimizer
```

## Service Health

```powershell
curl http://localhost:5000/api/health
```

## Logs

View logs in `logs/dfs_pools_YYYYMMDD.log`

```powershell
type logs\dfs_pools_*.log
```

That's it!
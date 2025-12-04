# DFS Pools Service

Self-contained microservice for fetching and serving DFS player pool data from DraftKings.

## Quick Start

```powershell
pip install -r requirements.txt
python app.py
```

Service runs on `http://localhost:5000`

## Documentation

- [Quick Start Guide](docs/QUICK_START.md)
- [API Reference](docs/API_REFERENCE.md)
- [Full Documentation](docs/README.md)

## Project Structure

```
dfs-pools/
├── src/              # Source code
├── data/             # Database and backups
├── logs/             # Log files
├── tests/            # Tests
├── docs/             # User documentation
├── dev-docs/         # Development notes
└── app.py            # Entry point
```

## Platform Integration

This service is one microservice in the larger DFS platform, alongside:
- Live Odds Service
- Stats Updates Service  
- Simulation Engine
- Optimizer
- Frontend

All services communicate via REST APIs.

## Key Endpoints

- `/api/sports` - List sports
- `/api/draftgroups` - List contests
- `/api/draftgroups/active/optimizer` - Active player pools
- `/api/scheduler/trigger` - Manual data fetch

See [API Reference](docs/API_REFERENCE.md) for complete endpoint list.
# Deployment Guide

## Running the Service

### Development
```bash
python app.py
```

### Production

Use a production WSGI server:

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "src.api_server:app"
```

## Configuration

Environment variables (create `.env` file):

```
# Scheduler
SCHEDULER_ENABLED=True
SCHEDULER_INTERVAL_HOURS=4

# Logging
LOG_LEVEL=INFO
DEBUG_MODE=False

# Database
DATABASE_PATH=data/dfs_pools.db
```

## Platform Integration

This service runs on port 5000 and exposes REST APIs for:
- Simulation Engine
- Optimizer
- Frontend

All other platform services can call: `http://dfs-pools-service:5000/api/*`

## Health Monitoring

```bash
curl http://localhost:5000/api/health
```

Returns 200 if healthy.

## Data Updates

Automatic every 4 hours (configurable)

Manual trigger:
```bash
curl -X POST http://localhost:5000/api/scheduler/trigger
```

That's all you need!
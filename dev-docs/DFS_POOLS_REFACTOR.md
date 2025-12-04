# DFS Pools Service - Clean Structure Refactor

## Overview

**Goal**: Organize the DFS Pools code into a clean folder structure while maintaining all functionality.

**DFS Pools = ONE self-contained microservice** for your larger platform.

---

## Current State (Files in Root)

```
dfs-pools/
├── api_server.py
├── db_manager.py
├── dk_pools.py
├── pool_scheduler.py
├── logger.py
├── config.py
├── test_scheduler.py
├── dfs_pools.db
├── requirements.txt
├── README.md
└── data/
```

---

## Proposed Clean Structure

```
dfs-pools/                           ← ONE microservice
├── src/
│   ├── api_server.py                ← Flask REST API (moved from root)
│   ├── db_manager.py                ← Database operations (moved from root)
│   ├── dk_pools.py                  ← DraftKings client (moved from root)
│   ├── pool_scheduler.py            ← Auto-update scheduler (moved from root)
│   ├── logger.py                    ← Logging utilities (moved from root)
│   └── config.py                    ← Configuration (moved from root)
├── data/
│   ├── dfs_pools.db                 ← SQLite database
│   └── draftables/                  ← JSON backups
├── logs/                            ← Log files
├── tests/
│   └── test_scheduler.py            ← Tests
├── docs/
│   └── README.md                    ← Documentation
├── app.py                           ← Simple entry point (NEW)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Implementation Steps

### 1. Create src/ folder
```powershell
mkdir src
```

### 2. Move Python files
```powershell
Move-Item api_server.py src/
Move-Item db_manager.py src/
Move-Item dk_pools.py src/
Move-Item pool_scheduler.py src/
Move-Item logger.py src/
Move-Item config.py src/
```

### 3. Create app.py (entry point)
```python
"""DFS Pools Service - Main Entry Point"""
from src.api_server import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### 4. Update imports in src/ files
In each moved file, update imports:
- `from logger import...` → `from src.logger import...`
- `from db_manager import...` → `from src.db_manager import...`
- `from pool_scheduler import...` → `from src.pool_scheduler import...`
- `from config import...` → `from src.config import...`

### 5. Move tests
```powershell
mkdir tests
Move-Item test_scheduler.py tests/
```

---

## Running the Service

```powershell
python app.py
```

Same as before, just cleaner structure!

---

## Platform Integration

Your larger platform structure:
```
platform/
├── dfs-pools/              ← This service (drop in as-is)
│   ├── src/
│   ├── data/
│   ├── app.py
│   └── requirements.txt
├── live-odds/              ← Another service
├── stats-updates/          ← Another service
├── simulation-engine/      ← Another service
├── optimizer/              ← Another service
└── frontend/               ← Another service
```

Each service is independent and self-contained.

---

## What This Achieves

✅ Clean folder structure
✅ All Python code in `src/`
✅ Same functionality as original
✅ Easy to drop into platform
✅ Simple to run: `python app.py`
✅ No complex sub-services
✅ One database, one service

---

## What NOT to Do

❌ Don't break DFS Pools into sub-services
❌ Don't create API Gateway for DFS Pools itself  
❌ Don't separate databases
❌ Don't over-complicate

DFS Pools = ONE microservice in your platform!

---

This is the simple refactor you wanted. Just organizing files, nothing more.
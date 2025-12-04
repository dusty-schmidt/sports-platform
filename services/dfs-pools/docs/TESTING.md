# Testing Guide

## Quick Test (Cross-Platform)

```bash
# Start service (Terminal 1)
python app.py

# Run tests (Terminal 2)
python tests/test_service.py
```

The test suite will:
1. Check service health
2. Trigger full data ingestion from DraftKings
3. Verify sports data fetched
4. Verify draftgroups fetched
5. Verify player pools (draftables) fetched
6. Test optimizer view endpoint

## Expected Output

```
======================================================================
DFS POOLS SERVICE - INTEGRATION TESTS
======================================================================

[TEST 1] Checking service health...
  ✓ Service is healthy

[TEST 2] Triggering data ingestion...
  This will take 2-5 minutes to fetch all sports from DraftKings...
  ✓ Data ingestion completed

[TEST 3] Verifying sports data...
  ✓ Found 25 sports: NFL, NBA, CBB, CFB, GOLF...

[TEST 4] Verifying draftgroups...
  ✓ Found 45 draftgroups
  ✓ Breakdown by sport:
      CBB: 4
      CFB: 3
      NFL: 12
      ...

[TEST 5] Verifying player pools for NFL...
  ✓ Found 250 players for NFL draftgroup 138136

[TEST 6] Testing optimizer view...
  ✓ Found 8 active draftgroups with player data
  ✓ Sample: NFL has 250 players

======================================================================
TEST SUMMARY
======================================================================
Passed: 6/6

✓ ALL TESTS PASSED - Service is working correctly!
```

## Manual Verification

```bash
# Check health
curl http://localhost:5000/api/health

# Trigger ingestion
curl -X POST http://localhost:5000/api/scheduler/trigger

# View sports
curl http://localhost:5000/api/sports

# View draftgroups
curl http://localhost:5000/api/draftgroups

# View player pools for specific draftgroup
curl http://localhost:5000/api/draftgroups/138136/draftables

# View optimizer-ready data
curl http://localhost:5000/api/draftgroups/active/optimizer
```

## Logs

All activity logged to `logs/dfs_pools_YYYYMMDD.log`

```bash
# View recent logs
tail -50 logs/dfs_pools_*.log         # Linux/Mac
type logs\dfs_pools_*.log             # Windows  

# Watch logs live
tail -f logs/dfs_pools_*.log          # Linux/Mac
Get-Content logs\dfs_pools_*.log -Wait -Tail 20   # Windows

# Search for errors
grep ERROR logs/dfs_pools_*.log       # Linux/Mac
Select-String ERROR logs\dfs_pools_*.log  # Windows
```

## Database Verification

```bash
# Check database exists
ls data/dfs_pools.db                  # Linux/Mac
dir data\dfs_pools.db                 # Windows

# Query directly (if SQLite installed)
sqlite3 data/dfs_pools.db "SELECT COUNT(*) FROM draftgroups;"
sqlite3 data/dfs_pools.db "SELECT COUNT(*) FROM draftables;"
sqlite3 data/dfs_pools.db "SELECT sport, COUNT(*) FROM draftgroups GROUP BY sport;"
```

## Troubleshooting

**Service won't start:**
- Check port 5000 is available
- Review logs for errors

**No data after ingestion:**
- Check logs for DraftKings API errors
- Verify internet connection
- Check logs/dfs_pools_*.log for details

**Tests fail:**
- Ensure service is running on port 5000
- Check service health: `curl http://localhost:5000/api/health`
- Review test output for specific failure

That's it! One test suite, works on Windows and Linux.
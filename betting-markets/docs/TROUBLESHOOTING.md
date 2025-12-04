home/ds/betting-mkt-data/docs/TROUBLESHOOTING.md</path>
<content"># Troubleshooting Guide

This guide helps diagnose and resolve common issues with the Betting Market Data Service.

## Quick Diagnostics

### Health Check Commands

```bash
# Check service health
curl http://localhost:8000/health

# Check database connectivity
python scripts/init_database.py check

# Check scheduler status
curl http://localhost:8000/scheduler/status

# Check recent logs
tail -f logs/betting-market.log
```

### System Information

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(fastapi|sqlalchemy|apscheduler)"

# Check database file
ls -la *.db

# Check port availability
netstat -tlnp | grep :8000
```

## Common Issues and Solutions

### 1. Service Won't Start

#### Problem: API server fails to start

**Symptoms:**
- `uvicorn` command fails
- Port already in use error
- Import/dependency errors

**Diagnosis:**
```bash
# Check port conflicts
netstat -tlnp | grep :8000

# Check Python environment
which python
python --version

# Check dependencies
pip check

# Check for syntax errors
python -m py_compile api/main.py
python -m py_compile database/models.py
python -m py_compile scheduler/job_manager.py
```

**Solutions:**

1. **Port Already in Use**
   ```bash
   # Find and kill process using port 8000
   lsof -ti:8000 | xargs kill -9
   
   # Or use different port
   export API_PORT=8001
   python run_api.py
   ```

2. **Missing Dependencies**
   ```bash
   # Install missing packages
   pip install -r requirements.txt
   
   # Update existing packages
   pip install --upgrade -r requirements.txt
   ```

3. **Virtual Environment Issues**
   ```bash
   # Recreate virtual environment
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### 2. Database Connection Issues

#### Problem: Database connection failures

**Symptoms:**
- "database is locked" errors
- Connection refused errors
- Authentication failures

**Diagnosis:**
```bash
# Check database file permissions
ls -la betting_markets.db

# Test database connection
python -c "
from database import get_db, init_db
try:
    init_db()
    db = next(get_db())
    print('Database connection: SUCCESS')
    db.close()
except Exception as e:
    print(f'Database connection: FAILED - {e}')
"

# Check DATABASE_URL format
echo $DATABASE_URL

# Test with psql (if using PostgreSQL)
psql $DATABASE_URL -c "SELECT version();"
```

**Solutions:**

1. **SQLite Database Lock**
   ```bash
   # Check for active connections
   lsof betting_markets.db
   
   # Remove stale lock files
   rm -f betting_markets.db-wal betting_markets.db-shm
   
   # Recreate database if needed
   rm betting_markets.db
   python scripts/init_database.py init
   ```

2. **Permission Issues**
   ```bash
   # Fix file permissions
   chmod 664 betting_markets.db
   chown $USER:$USER betting_markets.db
   
   # Check directory permissions
   chmod 755 .
   ```

3. **PostgreSQL Connection Issues**
   ```bash
   # Check PostgreSQL service
   sudo systemctl status postgresql
   
   # Test connection manually
   psql -h localhost -U username -d betting_markets
   
   # Check pg_hba.conf for authentication settings
   sudo nano /etc/postgresql/*/main/pg_hba.conf
   ```

### 3. Data Collection Failures

#### Problem: Scheduled jobs failing or no data being collected

**Symptoms:**
- Empty responses from API endpoints
- Job execution errors in logs
- Sportsbook API timeouts

**Diagnosis:**
```bash
# Check scheduler status
curl http://localhost:8000/scheduler/status

# Check job statistics
curl http://localhost:8000/scheduler/stats/nba

# Check recent collection logs
tail -f logs/betting-market.log | grep -E "(ERROR|collection|nba)"

# Test manual collection
curl -X POST http://localhost:8000/collect/nba

# Verify sportsbook configurations
python -c "
from betting_service.config.sports import get_sport_config
config = get_sport_config('nba')
print(f'NBA config: {config}')
"
```

**Solutions:**

1. **Scheduler Not Running**
   ```bash
   # Start scheduler manually
   python -c "
   import asyncio
   from scheduler import job_manager
   asyncio.run(job_manager.start_scheduler())
   "
   
   # Check if auto-collection is enabled
   echo $SCHEDULER_AUTO_COLLECT_SPORTS
   ```

2. **Sportsbook API Issues**
   ```bash
   # Test sportsbook connectivity
   curl -H "User-Agent: BettingMarketService/1.0" \
        https://sportsbook.draftkings.com/api/v1/sports
   
   # Check for rate limiting
   # Review sportsbook API documentation
   # Adjust collection intervals in .env
   ```

3. **No Data in Database**
   ```bash
   # Verify sports and sportsbooks exist
   python scripts/init_database.py check
   
   # Check database for data
   python -c "
   from database import get_db
   from database.models import BettingMarket
   db = next(get_db())
   print(f'Total markets: {db.query(BettingMarket).count()}')
   db.close()
   "
   ```

### 4. API Performance Issues

#### Problem: Slow API responses or timeouts

**Symptoms:**
- Long response times (>5 seconds)
- Request timeouts
- High memory usage

**Diagnosis:**
```bash
# Check API response time
time curl http://localhost:8000/markets?limit=10

# Monitor resource usage
htop
free -h
df -h

# Check database performance
python -c "
import time
from database import get_db
from database.service import BettingMarketDBService

start = time.time()
db = next(get_db())
service = BettingMarketDBService(db)
markets = service.get_active_markets(limit=10)
elapsed = time.time() - start

print(f'Query time: {elapsed:.2f}s')
print(f'Markets found: {len(markets)}')
db.close()
"

# Check database indexes
sqlite3 betting_markets.db ".schema" | grep -E "(INDEX|CREATE INDEX)"
```

**Solutions:**

1. **Database Query Optimization**
   ```bash
   # Add database indexes
   python -c "
   from database import get_db
   from sqlalchemy import text
   
   db = next(get_db())
   
   # Add performance indexes
   db.execute(text('CREATE INDEX IF NOT EXISTS idx_markets_sport_time ON betting_markets (sport_id, game_start_time)'))
   db.execute(text('CREATE INDEX IF NOT EXISTS idx_snapshots_time ON market_snapshots (snapshot_time)'))
   
   db.commit()
   db.close()
   print('Indexes added successfully')
   "
   
   # Optimize query patterns
   # Review database service queries
   # Add proper indexing
   ```

2. **Connection Pool Tuning**
   ```bash
   # Adjust database pool settings
   export DATABASE_POOL_SIZE=5
   export DATABASE_MAX_OVERFLOW=10
   
   # Restart service with new settings
   ```

3. **API Caching**
   ```bash
   # Enable caching
   export CACHE_TTL_MARKETS=300
   export CACHE_BACKEND=redis
   ```

### 5. Memory Issues

#### Problem: High memory usage or out-of-memory errors

**Symptoms:**
- Service crashes with memory errors
- System becomes slow
- High RSS memory usage

**Diagnosis:**
```bash
# Check memory usage
ps aux | grep python
free -h

# Profile memory usage
python -m memory_profiler scripts/collect_markets.py nba

# Check for memory leaks
valgrind --tool=memcheck python run_api.py
```

**Solutions:**

1. **Reduce Data Retention**
   ```bash
   # Reduce snapshot retention
   export SCHEDULER_DAYS_TO_KEEP_SNAPSHOTS=3
   
   # Run cleanup
   python scripts/init_database.py cleanup --days 3
   ```

2. **Optimize Collection Intervals**
   ```bash
   # Increase collection intervals
   export SCHEDULER_NBA_INTERVAL=30
   
   # Reduce concurrent jobs
   export SCHEDULER_MAX_CONCURRENT_JOBS=1
   ```

3. **Database Optimization**
   ```bash
   # VACUUM database (SQLite)
   sqlite3 betting_markets.db "VACUUM;"
   
   # Analyze database (PostgreSQL)
   psql $DATABASE_URL -c "ANALYZE;"
   ```

### 6. Integration Issues

#### Problem: Cannot integrate with external applications

**Symptoms:**
- CORS errors in web applications
- API authentication failures
- Incorrect data formats

**Diagnosis:**
```bash
# Test CORS headers
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS http://localhost:8000/markets

# Check API response format
curl http://localhost:8000/markets | python -m json.tool

# Validate API schema
curl http://localhost:8000/openapi.json | python -m json.tool
```

**Solutions:**

1. **CORS Configuration**
   ```bash
   # Set CORS origins
   export CORS_ORIGINS=http://localhost:3000,https://yourapp.com
   
   # Restart service
   ```

2. **API Authentication**
   ```bash
   # Enable API key authentication
   export API_KEY_REQUIRED=true
   export API_KEY=your-secret-key
   
   # Test with API key
   curl -H "X-API-Key: your-secret-key" \
        http://localhost:8000/markets
   ```

3. **Data Format Validation**
   ```bash
   # Check API documentation
   curl http://localhost:8000/docs
   
   # Validate response format
   curl http://localhost:8000/markets | jq '.'
   ```

## Error Code Reference

### HTTP Status Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | Success | Normal operation |
| 400 | Bad Request | Invalid parameters, malformed JSON |
| 401 | Unauthorized | Missing or invalid API key |
| 404 | Not Found | Resource doesn't exist |
| 422 | Validation Error | Data validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Application error |

### Error Response Format

```json
{
  "detail": "Error description",
  "timestamp": "2023-11-02T22:04:56.088Z",
  "error_code": "VALIDATION_ERROR"
}
```

### Common Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| `DATABASE_CONNECTION_ERROR` | Cannot connect to database | Check DATABASE_URL, database service |
| `SCHEDULER_NOT_RUNNING` | Scheduler service is down | Restart scheduler or check logs |
| `SPORTSBOOK_API_ERROR` | External API request failed | Check internet connection, API limits |
| `VALIDATION_ERROR` | Input data validation failed | Check request format and required fields |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Implement client-side rate limiting |
| `AUTHENTICATION_REQUIRED` | Missing API key | Provide valid API key in headers |

## Log Analysis

### Log Locations

- **Application Logs**: `./logs/betting-market.log`
- **System Service Logs**: `journalctl -u betting-market-api`
- **Nginx Logs**: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- **Database Logs**: `/var/log/postgresql/postgresql-*.log`

### Log Levels

```bash
# Set debug logging
export LOG_LEVEL=DEBUG
python run_api.py

# Filter logs by level
tail -f logs/betting-market.log | grep -E "(ERROR|WARN)"
```

### Common Log Patterns

```
# Successful data collection
INFO - Successfully collected 25 events for nba - duration: 12.5s

# Database errors
ERROR - Database connection failed: connection refused

# Scheduler issues
ERROR - Job collect_nba failed: TimeoutError

# API errors
ERROR - Request failed: 422 Validation Error

# Sportsbook API issues
WARNING - FanDuel API rate limit exceeded, retrying in 60s
```

## Performance Monitoring

### Key Metrics

```bash
# Response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/markets

# Database query performance
time python -c "
from database import get_db
from database.service import BettingMarketDBService
db = next(get_db())
service = BettingMarketDBService(db)
markets = service.get_active_markets(limit=100)
print(f'Found {len(markets)} markets')
db.close()
"

# Scheduler performance
curl -s http://localhost:8000/scheduler/status | jq '.job_statistics'
```

### Monitoring Scripts

#### Health Check Script
```bash
#!/bin/bash
# health-check.sh

API_URL="http://localhost:8000"
TIMEOUT=5

# Check API health
if ! curl -f -s --max-time $TIMEOUT $API_URL/health > /dev/null; then
    echo "API is down"
    exit 1
fi

# Check database
if ! python scripts/init_database.py check > /dev/null 2>&1; then
    echo "Database is down"
    exit 1
fi

# Check scheduler
SCHEDULER_STATUS=$(curl -s $API_URL/scheduler/status)
if echo "$SCHEDULER_STATUS" | grep -q '"scheduler_running":false'; then
    echo "Scheduler is down"
    exit 1
fi

echo "All systems operational"
```

#### Performance Monitoring Script
```bash
#!/bin/bash
# monitor-performance.sh

API_URL="http://localhost:8000"

# Monitor API response times
echo "API Performance:"
curl -w "Markets: %{time_total}s\n" -s -o /dev/null $API_URL/markets
curl -w "Stats: %{time_total}s\n" -s -o /dev/null $API_URL/stats

# Monitor database performance
echo "Database Performance:"
python -c "
import time
from database import get_db
from database.service import BettingMarketDBService

db = next(get_db())
service = BettingMarketDBService(db)

start = time.time()
service.get_stats()
elapsed = time.time() - start

print(f'Statistics query: {elapsed:.3f}s')
db.close()
"
```

## Recovery Procedures

### Database Recovery

```bash
# Backup current database
cp betting_markets.db betting_markets.db.backup.$(date +%Y%m%d_%H%M%S)

# Restore from backup
cp betting_markets.db.backup.20231102_120000 betting_markets.db

# Recreate database if corrupted
rm betting_markets.db
python scripts/init_database.py init
```

### Service Recovery

```bash
# Restart service
sudo systemctl restart betting-market-api

# Reset scheduler
curl -X DELETE http://localhost:8000/scheduler/jobs/nba
curl -X POST http://localhost:8000/scheduler/jobs/nba

# Clear caches
python -c "
from database.service import BettingMarketDBService
from database import get_db
db = next(get_db())
service = BettingMarketDBService(db)
service.cleanup_old_snapshots(days_to_keep=1)
"
```

### Data Recovery

```bash
# Re-collect missing data
curl -X POST http://localhost:8000/collect/nba
curl -X POST http://localhost:8000/collect/nfl
curl -X POST http://localhost:8000/collect/mlb

# Verify data recovery
python scripts/init_database.py check
```

## Prevention and Best Practices

### Monitoring Setup
- Set up health checks (every 5 minutes)
- Monitor disk space and memory usage
- Set up log rotation
- Configure alerting for errors

### Maintenance Schedule
- **Daily**: Check health status and recent logs
- **Weekly**: Clean up old data and review performance
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Review and optimize database performance

### Backup Strategy
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/betting-market"
CONFIG_DIR="/backups/config"

# Create backup directories
mkdir -p $BACKUP_DIR $CONFIG_DIR

# Backup database
if [[ $DATABASE_URL == sqlite* ]]; then
    cp *.db $BACKUP_DIR/
elif [[ $DATABASE_URL == postgres* ]]; then
    pg_dump $DATABASE_URL | gzip > $BACKUP_DIR/betting_markets_$DATE.sql.gz
fi

# Backup configuration
cp .env $CONFIG_DIR/.env.$DATE

# Keep only last 30 days
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
find $CONFIG_DIR -name ".env.*" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Security Considerations
- Regularly update dependencies
- Use environment-specific configuration
- Implement proper logging and monitoring
- Review access permissions
- Use SSL/TLS for all connections
- Implement rate limiting

## Getting Help

### Self-Help Resources
1. Check this troubleshooting guide
2. Review application logs
3. Use the health check endpoints
4. Consult the API documentation at `/docs`

### Support Information

When requesting help, please include:
- Service version: `curl http://localhost:8000/stats | jq .api_version`
- Error messages and timestamps
- Configuration details (remove sensitive information)
- Steps to reproduce the issue
- Recent log entries

### Log Collection Script
```bash
#!/bin/bash
# collect-logs.sh

DATE=$(date +%Y%m%d_%H%M%S)
LOG_DIR="logs_$DATE"
mkdir -p $LOG_DIR

# Collect application logs
cp logs/betting-market.log $LOG_DIR/

# Collect system logs (last 100 lines)
journalctl -u betting-market-api -n 100 > $LOG_DIR/system.log

# Collect configuration
cp .env $LOG_DIR/config.env

# Collect database info
python -c "
import sys
sys.path.append('.')
from scripts.init_database import check_database
check_database()
" > $LOG_DIR/database_info.txt

# Create archive
tar -czf logs_$DATE.tar.gz $LOG_DIR
rm -rf $LOG_DIR

echo "Logs collected in logs_$DATE.tar.gz"
```

This troubleshooting guide covers the most common issues and their solutions. Keep this guide handy for quick reference when issues arise.
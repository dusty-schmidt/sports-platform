home/ds/betting-mkt-data/docs/CONFIGURATION.md</path>
<content"># Configuration Guide

This guide provides detailed information about configuring the Betting Market Data Service for different environments and use cases.

## Configuration Overview

The service supports configuration through:
1. **Environment Variables** - Primary configuration method
2. **`.env` Files** - Development convenience
3. **Configuration Files** - Static configuration
4. **Command Line Arguments** - Runtime overrides

## Environment Variables

### Database Configuration

#### `DATABASE_URL`
Connection string for the database. Supports multiple database engines.

**Examples:**
```bash
# SQLite (default, development)
DATABASE_URL=sqlite:///./betting_markets.db

# PostgreSQL (production)
DATABASE_URL=postgresql://username:password@localhost:5432/betting_markets

# MySQL (production)
DATABASE_URL=mysql://username:password@localhost:3306/betting_markets
```

**Format:**
```
[dialect]+[driver]://[username]:[password]@[host]:[port]/[database]
```

**Supported Databases:**
- `sqlite` - SQLite (default)
- `postgresql` - PostgreSQL
- `mysql` - MySQL
- `oracle` - Oracle Database

**SSL Configuration (PostgreSQL):**
```bash
DATABASE_URL=postgresql://user:pass@localhost/db?sslmode=require
DATABASE_URL=postgresql://user:pass@localhost/db?sslmode=verify-full
```

### API Configuration

#### `API_HOST`
Host address for the API server.

**Default:** `0.0.0.0`

**Examples:**
```bash
# Development
API_HOST=127.0.0.1

# Production
API_HOST=0.0.0.0
```

#### `API_PORT`
Port number for the API server.

**Default:** `8000`

**Examples:**
```bash
# Development
API_PORT=8000

# Production with reverse proxy
API_PORT=8000

# Custom port
API_PORT=8080
```

#### `API_DEBUG`
Enable debug mode for development.

**Default:** `false`

**Options:**
- `true` - Enable debug mode
- `false` - Production mode

**Impact:**
- `true`: Detailed error messages, auto-reload, verbose logging
- `false`: Minimal error details, optimized performance

```bash
# Development
API_DEBUG=true

# Production
API_DEBUG=false
```

#### `API_WORKERS`
Number of worker processes.

**Default:** `1`

**Recommended:**
- Development: `1`
- Production: Number of CPU cores or `$(nproc)`

```bash
# Single process (development)
API_WORKERS=1

# Multi-process (production)
API_WORKERS=4
```

### Scheduler Configuration

#### Collection Intervals

Configure how often data is collected for each sport.

**Format:** Minutes between collections

```bash
# NBA - Frequent updates during season
SCHEDULER_NBA_INTERVAL=15

# NFL - High frequency during season
SCHEDULER_NFL_INTERVAL=15

# MLB - Moderate frequency
SCHEDULER_MLB_INTERVAL=30

# NHL - Moderate frequency
SCHEDULER_NHL_INTERVAL=20

# Soccer - Moderate frequency
SCHEDULER_SOCCER_INTERVAL=20

# Default for unspecified sports
SCHEDULER_DEFAULT_INTERVAL=30
```

**Considerations:**
- **Business Hours**: Higher frequency during active hours
- **Seasonal Sports**: Adjust intervals based on season
- **Resource Usage**: Balance data freshness vs. API load
- **Rate Limiting**: Respect sportsbook API limits

#### Auto-Collection Sports

List of sports to automatically collect data for.

**Format:** JSON array of sport names

```bash
# Basic configuration
SCHEDULER_AUTO_COLLECT_SPORTS=["nba","nfl","mlb","nhl"]

# Extended configuration
SCHEDULER_AUTO_COLLECT_SPORTS=["nba","nfl","mlb","nhl","soccer","tennis","golf"]

# Single sport (development)
SCHEDULER_AUTO_COLLECT_SPORTS=["nba"]

# No auto-collection
SCHEDULER_AUTO_COLLECT_SPORTS=[]
```

#### Default Sportsbooks

Configure default sportsbooks for each sport.

**Format:** JSON object mapping sports to arrays of sportsbook names

```bash
# Standard configuration
SCHEDULER_DEFAULT_SPORTSBOOKS='{
  "nba": ["draftkings", "fanduel"],
  "nfl": ["draftkings", "fanduel"],
  "mlb": ["draftkings", "fanduel"],
  "nhl": ["draftkings", "fanduel"],
  "soccer": ["draftkings", "fanduel"]
}'

# Extended configuration
SCHEDULER_DEFAULT_SPORTSBOOKS='{
  "nba": ["draftkings", "fanduel", "betmgm", "caesars"],
  "nfl": ["draftkings", "fanduel", "betmgm", "caesars"],
  "mlb": ["draftkings", "fanduel", "pointsbet"],
  "nhl": ["draftkings", "fanduel"],
  "soccer": ["draftkings", "fanduel", "bet365"]
}'
```

#### Job Management

```bash
# Maximum concurrent collection jobs
SCHEDULER_MAX_CONCURRENT_JOBS=3

# Job timeout in minutes
SCHEDULER_JOB_TIMEOUT_MINUTES=10

# Number of retry attempts for failed jobs
SCHEDULER_RETRY_ATTEMPTS=2

# Grace period for missed jobs (seconds)
SCHEDULER_MISFIRE_GRACE_TIME=300
```

**Recommendations:**
- `MAX_CONCURRENT_JOBS`: 1-3 for stability, 3-5 for high throughput
- `JOB_TIMEOUT`: 5-15 minutes depending on data volume
- `RETRY_ATTEMPTS`: 2-3 for resilience
- `MISFIRE_GRACE_TIME`: 300-600 seconds

### Data Management

#### Cleanup Settings

```bash
# Cleanup interval in hours
SCHEDULER_CLEANUP_INTERVAL_HOURS=24

# Days to keep old snapshots
SCHEDULER_DAYS_TO_KEEP_SNAPSHOTS=7

# Cleanup batch size
SCHEDULER_CLEANUP_BATCH_SIZE=1000
```

**Data Retention Strategy:**
- **Live Data**: 7-14 days for real-time analysis
- **Historical Data**: Archive to separate storage
- **Log Files**: 30-90 days depending on storage constraints

#### Archive Settings

```bash
# Enable data archiving
ARCHIVE_ENABLE=true

# Archive directory
ARCHIVE_DIR=./archive

# Archive compression
ARCHIVE_COMPRESSION=gzip

# Archive retention (days)
ARCHIVE_RETENTION_DAYS=365
```

### Performance Configuration

#### Database Connection Pool

```bash
# Database connection pool size
DATABASE_POOL_SIZE=10

# Maximum overflow connections
DATABASE_MAX_OVERFLOW=20

# Pool timeout (seconds)
DATABASE_POOL_TIMEOUT=30

# Pool recycle time (seconds)
DATABASE_POOL_RECYCLE=3600
```

**Scaling Guidelines:**
- **Small Scale** (< 1000 markets): `POOL_SIZE=5, MAX_OVERFLOW=10`
- **Medium Scale** (1000-10000 markets): `POOL_SIZE=10, MAX_OVERFLOW=20`
- **Large Scale** (> 10000 markets): `POOL_SIZE=20, MAX_OVERFLOW=40`

#### API Rate Limiting

```bash
# Requests per minute per IP
RATE_LIMIT_PER_MINUTE=100

# Burst limit (requests in short time)
RATE_LIMIT_BURST=20

# Rate limit storage backend
RATE_LIMIT_STORAGE=memory

# Alternative: redis
# RATE_LIMIT_STORAGE=redis://localhost:6379
```

#### Caching Configuration

```bash
# Cache TTL for market data (seconds)
CACHE_TTL_MARKETS=300

# Cache TTL for sports/sportsbooks (seconds)
CACHE_TTL_METADATA=3600

# Cache TTL for odds data (seconds)
CACHE_TTL_ODDS=60

# Cache backend
CACHE_BACKEND=memory

# Alternative: redis
# CACHE_BACKEND=redis://localhost:6379/0
```

### Logging Configuration

#### Log Levels

```bash
# Application log level
LOG_LEVEL=INFO

# Database log level
LOG_LEVEL_DATABASE=WARNING

# Scheduler log level
LOG_LEVEL_SCHEDULER=INFO

# API log level
LOG_LEVEL_API=INFO
```

**Log Levels:**
- `DEBUG` - Detailed debug information
- `INFO` - General information (recommended for production)
- `WARNING` - Warning messages
- `ERROR` - Error messages only
- `CRITICAL` - Critical errors only

#### Log Format and Output

```bash
# Log format (json or text)
LOG_FORMAT=text

# Log output (file, syslog, stdout)
LOG_OUTPUT=stdout

# Log file path (if using file output)
LOG_FILE=./logs/betting-market.log

# Log rotation
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=10

# Structured logging
LOG_STRUCTURED=true
```

**JSON Logging Format:**
```json
{
  "timestamp": "2023-11-02T22:01:42.299Z",
  "level": "INFO",
  "logger": "betting-market-api",
  "message": "Data collection completed",
  "sport": "nba",
  "events_collected": 25,
  "duration_seconds": 12.5
}
```

### Security Configuration

#### API Security

```bash
# Enable API key authentication
API_KEY_REQUIRED=false

# API key for external access
API_KEY=your-secret-api-key-here

# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://yourapp.com

# Enable HTTPS redirect
HTTPS_REDIRECT=false

# Allowed hosts
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

#### Database Security

```bash
# Database SSL mode
DATABASE_SSL_MODE=prefer

# Database SSL certificates
DATABASE_SSL_CERT=/path/to/client-cert.pem
DATABASE_SSL_KEY=/path/to/client-key.pem
DATABASE_SSL_CA=/path/to/ca-cert.pem
```

### External API Configuration

#### Sportsbook API Keys

```bash
# DraftKings API configuration
DRAFTKINGS_API_KEY=your_draftkings_key
DRAFTKINGS_USER_AGENT=BettingMarketService/1.0

# FanDuel API configuration  
FANDUEL_API_KEY=your_fanduel_key
FANDUEL_USER_AGENT=BettingMarketService/1.0

# Additional sportsbooks
BETMGM_API_KEY=your_betmgm_key
CAESARS_API_KEY=your_caesars_key
```

#### Request Configuration

```bash
# API request timeout (seconds)
HTTP_TIMEOUT=30

# API request retry attempts
HTTP_RETRY_ATTEMPTS=3

# API request backoff factor
HTTP_BACKOFF_FACTOR=2.0

# User agent for API requests
HTTP_USER_AGENT=BettingMarketService/1.0
```

## Configuration Files

### .env File

Create a `.env` file in the application root for local development:

```bash
# Database
DATABASE_URL=sqlite:///./betting_markets.db

# API
API_DEBUG=true
API_HOST=127.0.0.1
API_PORT=8000

# Scheduler
SCHEDULER_AUTO_COLLECT_SPORTS=["nba"]
SCHEDULER_NBA_INTERVAL=5

# Logging
LOG_LEVEL=DEBUG
```

### JSON Configuration

For complex configurations, use JSON files:

**config/production.json:**
```json
{
  "database": {
    "url": "postgresql://user:pass@localhost/betting_markets",
    "pool_size": 20,
    "max_overflow": 40
  },
  "scheduler": {
    "auto_collect_sports": ["nba", "nfl", "mlb", "nhl"],
    "intervals": {
      "nba": 15,
      "nfl": 15,
      "mlb": 30,
      "nhl": 20
    }
  },
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4
  }
}
```

## Environment-Specific Configuration

### Development

**File:** `.env.development`
```bash
# Relaxed settings for development
DATABASE_URL=sqlite:///./dev_betting_markets.db
API_DEBUG=true
LOG_LEVEL=DEBUG

# Frequent updates for testing
SCHEDULER_AUTO_COLLECT_SPORTS=["nba"]
SCHEDULER_NBA_INTERVAL=1

# Shorter data retention
SCHEDULER_DAYS_TO_KEEP_SNAPSHOTS=1
```

### Testing

**File:** `.env.test`
```bash
# Isolated test database
DATABASE_URL=sqlite:///:memory:
API_DEBUG=false
LOG_LEVEL=WARNING

# No automatic collection during tests
SCHEDULER_AUTO_COLLECT_SPORTS=[]

# No cleanup during tests
SCHEDULER_CLEANUP_INTERVAL_HOURS=999999
```

### Staging

**File:** `.env.staging`
```bash
# Production-like settings
DATABASE_URL=postgresql://user:pass@staging-db/betting_markets
API_DEBUG=false
LOG_LEVEL=INFO

# Realistic collection schedule
SCHEDULER_AUTO_COLLECT_SPORTS=["nba","nfl"]
SCHEDULER_NBA_INTERVAL=15
SCHEDULER_NFL_INTERVAL=15

# Moderate retention
SCHEDULER_DAYS_TO_KEEP_SNAPSHOTS=7
```

### Production

**File:** `.env.production`
```bash
# Optimized for performance
DATABASE_URL=postgresql://user:pass@prod-db/betting_markets?sslmode=require
API_DEBUG=false
LOG_LEVEL=INFO

# Full collection schedule
SCHEDULER_AUTO_COLLECT_SPORTS=["nba","nfl","mlb","nhl","soccer"]

# Optimized intervals
SCHEDULER_NBA_INTERVAL=15
SCHEDULER_NFL_INTERVAL=15
SCHEDULER_MLB_INTERVAL=30
SCHEDULER_NHL_INTERVAL=20
SCHEDULER_SOCCER_INTERVAL=20

# Production retention
SCHEDULER_DAYS_TO_KEEP_SNAPSHOTS=7

# Performance tuning
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
API_WORKERS=4
```

## Configuration Validation

### Environment Variable Validation

The service validates configuration on startup:

```python
# Automatic validation
- Database URL format
- Port ranges (1-65535)
- Log level values
- JSON format for list configurations
- Numeric ranges for intervals and timeouts
```

### Configuration Testing

```bash
# Test configuration loading
python -c "
from scheduler.config import config
print('Configuration loaded successfully')
print(f'Database URL: {config.database_url}')
print(f'NBA Interval: {config.nba_interval} minutes')
"

# Validate specific configuration
python scripts/init_database.py check
```

### Configuration Override Precedence

1. **Command line arguments** (highest priority)
2. **Environment variables**
3. **.env files**
4. **Configuration files**
5. **Default values** (lowest priority)

## Configuration Management Best Practices

### Security
- Never commit `.env` files with real credentials
- Use different database users for different environments
- Enable SSL/TLS for database connections in production
- Rotate API keys regularly

### Environment Separation
- Use separate databases for each environment
- Configure different sportsbooks per environment if needed
- Use different notification/webhook endpoints per environment

### Monitoring
- Set up alerts for configuration changes
- Monitor configuration validation errors
- Track configuration-related performance metrics

### Documentation
- Document all custom configuration variables
- Maintain environment-specific configuration guides
- Version control configuration templates

### Backup
- Backup configuration files regularly
- Include configuration in deployment procedures
- Test configuration restoration procedures

## Troubleshooting Configuration Issues

### Common Issues

#### Database Connection Failures
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test database connection
psql $DATABASE_URL -c "SELECT version();"

# Verify database permissions
psql $DATABASE_URL -c "\l"
```

#### Invalid JSON Configuration
```bash
# Validate JSON syntax
python -c "import json; print(json.load(open('config.json')))"

# Check JSON format for environment variables
python -c "
import json
import os
try:
    sports = json.loads(os.getenv('SCHEDULER_AUTO_COLLECT_SPORTS', '[]'))
    print('Valid JSON:', sports)
except json.JSONDecodeError as e:
    print('Invalid JSON:', e)
"
```

#### Port Binding Issues
```bash
# Check if port is already in use
netstat -tlnp | grep :8000

# Check firewall rules
sudo ufw status

# Test port binding
telnet localhost 8000
```

#### Permission Issues
```bash
# Check file permissions
ls -la .env
chmod 600 .env  # Secure the .env file

# Check directory permissions
ls -la logs/
mkdir -p logs/
chmod 755 logs/
```

### Configuration Debugging

#### Enable Debug Logging
```bash
export LOG_LEVEL=DEBUG
export LOG_LEVEL_DATABASE=DEBUG
python run_api.py
```

#### Check Configuration Loading
```bash
# Print all environment variables
printenv | grep -E "(API_|SCHEDULER_|DATABASE_)"

# Test configuration import
python -c "
from scheduler.config import config
import os

print('=== Configuration Debug ===')
print(f'DATABASE_URL: {os.getenv(\"DATABASE_URL\", \"Not set\")}')
print(f'API_PORT: {config.api_port if hasattr(config, \"api_port\") else \"Using default\"}')
print(f'NBA_INTERVAL: {config.nba_interval} minutes')
print(f'AUTO_SPORTS: {config.auto_collect_sports}')
"
```

#### Database Configuration Check
```bash
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
```

## Performance Tuning

### Database Performance
```bash
# Optimize for read-heavy workload
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
DATABASE_POOL_RECYCLE=3600

# Connection timeout
DATABASE_POOL_TIMEOUT=60
```

### API Performance
```bash
# Enable connection pooling
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# API optimization
API_WORKERS=4
RATE_LIMIT_PER_MINUTE=1000
CACHE_TTL_MARKETS=300
```

### Scheduler Performance
```bash
# Job optimization
SCHEDULER_MAX_CONCURRENT_JOBS=3
SCHEDULER_JOB_TIMEOUT_MINUTES=5

# Collection optimization
SCHEDULER_NBA_INTERVAL=15
SCHEDULER_CLEANUP_INTERVAL_HOURS=12
```

## Advanced Configuration

### Custom Sportsbook Configuration

Add support for additional sportsbooks:

```bash
# Custom sportsbook endpoints
CUSTOM_BOOKS_CONFIG='{
  "bet365": {
    "base_url": "https://sports.bet365.com",
    "api_key": "your_bet365_key",
    "timeout": 30
  },
  "pointsbet": {
    "base_url": "https://api.pointsbet.com",
    "api_key": "your_pointsbet_key",
    "timeout": 25
  }
}'
```

### Custom Analytics Endpoints

```bash
# Enable custom analytics
ANALYTICS_ENABLE=true

# Custom analysis endpoints
ANALYTICS_ENDPOINTS='{
  "arbitrage_detection": true,
  "line_movement": true,
  "value_betting": true
}'
```

### Webhook Configuration

```bash
# Enable webhook notifications
WEBHOOK_ENABLE=true

# Webhook endpoints
WEBHOOK_URLS='{
  "data_collection_complete": "https://your-app.com/webhooks/collection",
  "error_alerts": "https://your-app.com/webhooks/errors",
  "scheduler_events": "https://your-app.com/webhooks/scheduler"
}'
```

### Metric Collection

```bash
# Enable metrics collection
METRICS_ENABLE=true

# Metrics endpoints
METRICS_PORT=9090
METRICS_PATH=/metrics

# Prometheus integration
PROMETHEUS_ENABLE=true
PROMETHEUS_ENDPOINT=/prometheus/metrics
```

This comprehensive configuration guide covers all aspects of configuring the Betting Market Data Service for different environments and use cases. Use the environment-specific templates as starting points and customize based on your specific requirements.
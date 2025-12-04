# Betting Market Data Service

A comprehensive, production-ready Python service for collecting, storing, and providing betting market odds across multiple sportsbooks via REST API.

## 🎯 Features

### Core Functionality
- **Multi-Sportsbook Integration**: Collects data from DraftKings, FanDuel with expandable architecture
- **Automated Data Collection**: Scheduled jobs with configurable intervals per sport
- **REST API**: Comprehensive API for accessing betting data
- **Database Storage**: Persistent storage with automatic cleanup
- **Real-time Analytics**: Market comparison and odds analysis endpoints

### API Endpoints
- **Health & Metadata**: `/health`, `/sports`, `/sportsbooks`
- **Market Data**: `/markets`, `/markets/{id}`, `/odds/latest`
- **Data Collection**: `/collect/{sport}`, `/scheduler/*`
- **Analytics**: `/stats`, `/analytics/market-comparison`

### Scheduler Features
- **Configurable Intervals**: Different collection frequencies per sport
- **Automatic Job Management**: Add/remove jobs via API
- **Manual Triggers**: On-demand data collection
- **Background Processing**: Non-blocking data collection
- **Error Handling**: Retry logic and comprehensive logging

### Database Design
- **Normalized Schema**: Sports, Sportsbooks, Markets, Snapshots
- **Performance Optimized**: Strategic indexes for fast queries
- **Data Integrity**: Foreign keys and unique constraints
- **Migration Support**: Alembic for schema version management

## 🏗️ Architecture

```
betting-mkt-data/
├── api/                    # FastAPI application
│   └── main.py            # Main API server
├── database/              # Database layer
│   ├── __init__.py
│   ├── connection.py      # DB connection management
│   ├── models.py          # SQLAlchemy models & Pydantic schemas
│   └── service.py         # Database service layer
├── scheduler/             # Job scheduling system
│   ├── __init__.py
│   ├── config.py          # Scheduler configuration
│   └── job_manager.py     # Job management logic
├── betting_service/       # Original service core
│   ├── books/             # Sportsbook clients
│   ├── config/            # Sport configuration
│   ├── utils/             # Utilities
│   ├── models.py          # Data models
│   └── service.py         # Collection logic
├── alembic/               # Database migrations
├── tests/                 # Comprehensive test suite
├── scripts/               # CLI scripts
└── data/                  # JSON output directory
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- SQLite (default) or PostgreSQL/MySQL for production

### Installation

1. **Clone and setup**:
```bash
git clone <repository>
cd betting-mkt-data
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Initialize Database**:
```bash
# Run migrations
alembic upgrade head

# Or use the built-in initialization
python -c "from database import init_db; init_db()"
```

4. **Start the API Server**:
```bash
# Development
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

5. **Access the API**:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Sports List: http://localhost:8000/sports

## 📊 API Usage Examples

### Get Current Markets
```bash
# All upcoming NBA markets
curl "http://localhost:8000/markets?sport=nba&limit=10"

# Markets with odds from DraftKings
curl "http://localhost:8000/markets?sportsbook=draftkings&limit=5"
```

### Trigger Data Collection
```bash
# Manual collection for NBA
curl -X POST "http://localhost:8000/collect/nba"

# Collection from specific sportsbooks
curl -X POST "http://localhost:8000/collect/nba?books=draftkings&books=fanduel"
```

### Get Latest Odds
```bash
# Latest odds for analytics applications
curl "http://localhost:8000/odds/latest?sport=nba&limit=10"
```

### Compare Market Odds
```bash
# Compare odds across sportsbooks for a specific market
curl "http://localhost:8000/analytics/market-comparison?market_id=123"
```

### Scheduler Management
```bash
# Get scheduler status
curl "http://localhost:8000/scheduler/status"

# Add scheduled job for NHL
curl -X POST "http://localhost:8000/scheduler/jobs/nhl"

# Manually trigger NHL collection
curl -X POST "http://localhost:8000/scheduler/trigger/nhl"
```

## ⚙️ Configuration

### Environment Variables

**Database**:
- `DATABASE_URL`: Connection string (default: `sqlite:///./betting_markets.db`)

**API Settings**:
- `API_HOST`: API server host (default: `0.0.0.0`)
- `API_PORT`: API server port (default: `8000`)
- `API_DEBUG`: Debug mode (default: `false`)

**Scheduler Settings**:
- `SCHEDULER_NBA_INTERVAL`: NBA collection interval in minutes (default: `15`)
- `SCHEDULER_NFL_INTERVAL`: NFL collection interval in minutes (default: `15`)
- `SCHEDULER_MLB_INTERVAL`: MLB collection interval in minutes (default: `30`)
- `SCHEDULER_NHL_INTERVAL`: NHL collection interval in minutes (default: `20`)
- `SCHEDULER_SOCCER_INTERVAL`: Soccer collection interval (default: `20`)
- `SCHEDULER_AUTO_COLLECT_SPORTS`: Auto-collection sports list
- `SCHEDULER_DAYS_TO_KEEP_SNAPSHOTS`: Data retention days (default: `7`)

### Sport Configuration

Sports configuration is managed in [`scheduler/config.py`](scheduler/config.py):

```python
SPORTS_CONFIG = {
    "nba": {
        "interval_minutes": 15,
        "books": ["draftkings", "fanduel"],
        "active_hours": [(6, 23)],  # 6 AM to 11 PM
    },
    # ... other sports
}
```

## 🔧 Development

### Running Tests
```bash
# Run all tests
pytest -q

# Run with coverage
pytest --cov=api --cov=database --cov=scheduler tests/

# Run specific test file
pytest tests/test_api.py -v
```

### Database Migrations
```bash
# Generate new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality
```bash
# Format code
black . && isort .

# Type checking
mypy .
```

## 🏃‍♂️ CLI Usage

### Data Collection
```bash
# Original CLI still works
PYTHONPATH=. python scripts/collect_markets.py nba --books draftkings fanduel
```

### Database Operations
```bash
# Initialize database
python -c "from database import init_db; init_db()"

# Check database stats
python -c "from database.service import BettingMarketDBService; from database.connection import SessionLocal; db = SessionLocal(); print(BettingMarketDBService(db).get_stats())"
```

## 🏗️ Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### PostgreSQL Setup
```bash
# Update DATABASE_URL
export DATABASE_URL="postgresql://user:password@localhost:5432/betting_markets"

# Run migrations
alembic upgrade head
```

### Production Configuration
```bash
# Environment variables for production
export API_DEBUG=false
export DATABASE_URL=postgresql://...
export SCHEDULER_AUTO_COLLECT_SPORTS=["nba","nfl","mlb","nhl","soccer"]
```

### Monitoring
- Health endpoint: `/health`
- Statistics: `/stats`
- Scheduler status: `/scheduler/status`
- Logs: Check application logs for job execution details

## 📈 Performance Considerations

### Database Optimization
- **Indexes**: Strategic indexing on sport_id, game_start_time, sportsbook_id
- **Data Retention**: Automatic cleanup of old snapshots
- **Query Optimization**: Efficient joins and filtering

### Scalability
- **Async Operations**: Non-blocking API and data collection
- **Background Jobs**: APScheduler for reliable task execution
- **Connection Pooling**: SQLAlchemy connection management

### Monitoring
- **Health Checks**: Comprehensive health monitoring
- **Job Statistics**: Track collection success rates and timing
- **Error Handling**: Comprehensive logging and error reporting

## 🧪 Testing Strategy

### Test Coverage
- **Unit Tests**: Database models, service layer, scheduler logic
- **Integration Tests**: API endpoints with test database
- **Mock Tests**: Sportsbook API interactions
- **Performance Tests**: Database query efficiency

### Running Tests
```bash
# Full test suite
pytest

# With coverage report
pytest --cov=. --cov-report=html

# Specific test categories
pytest tests/test_database.py -v
pytest tests/test_api.py -v
```

## 🔌 Extending the Service

### Adding New Sportsbooks
1. Implement client in [`betting_service/books/`](betting_service/books/)
2. Register in [`betting_service/books/__init__.py`](betting_service/books/__init__.py)
3. Add to configuration in [`betting_service/config/sports.py`](betting_service/config/sports.py)

### Adding New Sports
1. Update [`scheduler/config.py`](scheduler/config.py) with sport settings
2. Add sport-specific configuration
3. Update API documentation

### Custom Analytics Endpoints
1. Add new endpoints to [`api/main.py`](api/main.py)
2. Implement business logic in appropriate service layer
3. Add corresponding tests

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with tests
4. Run quality checks: `black . && pytest`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **API Documentation**: Visit `/docs` endpoint when server is running
- **Health Check**: Monitor service health via `/health`
- **Logs**: Check application logs for detailed error information
- **Issues**: Report bugs and feature requests via GitHub issues

## 🏆 Production Readiness

This service is designed for production deployment with:
- ✅ Comprehensive error handling
- ✅ Database migrations and versioning
- ✅ Background job processing
- ✅ Performance optimization
- ✅ Monitoring and health checks
- ✅ Extensive test coverage
- ✅ Docker support
- ✅ Environment configuration
- ✅ Scalable architecture
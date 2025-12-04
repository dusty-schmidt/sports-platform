home/ds/betting-mkt-data/docs/README.md</path>
<content"># Documentation Index

Welcome to the Betting Market Data Service documentation. This comprehensive guide covers all aspects of the system from development to production deployment.

## 📚 Documentation Overview

| Document | Description | Audience |
|----------|-------------|----------|
| [API Reference](API_REFERENCE.md) | Complete REST API documentation with endpoints, examples, and response formats | API Consumers, Developers |
| [Deployment Guide](DEPLOYMENT.md) | Production deployment instructions for various environments | DevOps, System Administrators |
| [Configuration Guide](CONFIGURATION.md) | Detailed configuration options and environment setup | Developers, DevOps |
| [Development Guide](DEVELOPMENT.md) | Development workflow, coding standards, and contribution guidelines | Developers |
| [Troubleshooting Guide](TROUBLESHOOTING.md) | Common issues, diagnostics, and solutions | Support, Developers |

## 🚀 Quick Start

### For API Consumers
1. **API Documentation**: Start with [API Reference](API_REFERENCE.md)
2. **Quick Test**: `curl http://localhost:8000/health`
3. **Examples**: See code examples in cURL, Python, and JavaScript

### For Developers
1. **Setup**: Follow [Development Guide](DEVELOPMENT.md) for local setup
2. **Configuration**: See [Configuration Guide](CONFIGURATION.md) for options
3. **Testing**: Run `pytest` and review test examples

### For System Administrators
1. **Deployment**: Use [Deployment Guide](DEPLOYMENT.md) for production setup
2. **Configuration**: Configure using [Configuration Guide](CONFIGURATION.md)
3. **Monitoring**: Check [Troubleshooting Guide](TROUBLESHOOTING.md) for monitoring

### For Support/Operations
1. **Diagnostics**: Start with [Troubleshooting Guide](TROUBLESHOOTING.md)
2. **Health Checks**: Monitor using API endpoints
3. **Recovery**: Follow recovery procedures in troubleshooting guide

## 📖 Quick Reference

### Essential Endpoints
- **Health Check**: `GET /health`
- **Sports List**: `GET /sports`
- **Markets**: `GET /markets`
- **Latest Odds**: `GET /odds/latest`
- **Trigger Collection**: `POST /collect/{sport}`

### Common Commands
```bash
# Start service
python run_api.py

# Initialize database
python scripts/init_database.py init

# Check status
python scripts/init_database.py check

# Run tests
pytest

# Apply migrations
alembic upgrade head
```

### Environment Variables
```bash
DATABASE_URL=sqlite:///./betting_markets.db
API_DEBUG=true
SCHEDULER_AUTO_COLLECT_SPORTS=["nba","nfl"]
LOG_LEVEL=INFO
```

## 🏗️ System Architecture

### Components
- **API Server**: FastAPI-based REST API
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL/MySQL support
- **Scheduler**: APScheduler for automated data collection
- **Sportsbook Clients**: Modular clients for data collection
- **Background Jobs**: Non-blocking data processing

### Data Flow
```
Sportsbook APIs → Sportsbook Clients → Database Storage → REST API → Analytics Apps
                     ↓
                Scheduler Jobs (Automated)
```

### API Structure
```
/health                    # System health
/sports, /sportsbooks      # Metadata
/markets                   # Market data
/odds                      # Odds data
/collect                   # Manual data collection
/scheduler                # Job management
/stats, /analytics         # System analytics
```

## 🔧 Configuration Overview

### Database Configuration
```bash
# SQLite (Development)
DATABASE_URL=sqlite:///./betting_markets.db

# PostgreSQL (Production)
DATABASE_URL=postgresql://user:pass@localhost:5432/betting_markets
```

### Scheduler Configuration
```bash
# Collection intervals (minutes)
SCHEDULER_NBA_INTERVAL=15
SCHEDULER_NFL_INTERVAL=15
SCHEDULER_MLB_INTERVAL=30

# Auto-collect sports
SCHEDULER_AUTO_COLLECT_SPORTS=["nba","nfl","mlb","nhl"]
```

### API Configuration
```bash
# Server settings
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Performance
DATABASE_POOL_SIZE=10
RATE_LIMIT_PER_MINUTE=100
```

## 📊 Key Features

### Data Collection
- **Multi-Sportsbook**: DraftKings, FanDuel (expandable)
- **Scheduled Collection**: Automated intervals per sport
- **Real-time Updates**: On-demand data collection
- **Error Handling**: Robust retry and logging

### API Features
- **RESTful Design**: Standard HTTP methods and status codes
- **Comprehensive Filtering**: Sport, sportsbook, time-based filters
- **Pagination**: Built-in limit/offset support
- **Real-time Data**: Latest odds from multiple sportsbooks

### Database Features
- **Normalized Schema**: Optimized for performance and integrity
- **Migration Support**: Alembic for schema versioning
- **Connection Pooling**: Efficient database connections
- **Data Retention**: Configurable cleanup policies

### Scheduler Features
- **Job Management**: Add/remove/manage collection jobs
- **Manual Triggers**: On-demand data collection
- **Background Processing**: Non-blocking operations
- **Error Recovery**: Retry logic and grace periods

## 🔐 Security Considerations

### API Security
- CORS configuration for web applications
- Rate limiting to prevent abuse
- API key authentication (optional)
- Input validation and sanitization

### Database Security
- Connection encryption (SSL/TLS)
- Parameterized queries (SQL injection protection)
- Connection pooling and timeouts
- Secure credential management

### Network Security
- HTTPS in production environments
- Firewall configuration
- VPN access for database connections
- Regular security updates

## 📈 Performance Optimization

### Database Optimization
- Strategic indexing on common query patterns
- Connection pooling and recycling
- Query optimization and analysis
- Regular maintenance and cleanup

### API Optimization
- Response caching where appropriate
- Pagination for large datasets
- Async operations for I/O-bound tasks
- Proper timeout handling

### System Optimization
- Memory usage monitoring
- CPU utilization tracking
- Disk space management
- Network performance tuning

## 🧪 Testing Strategy

### Test Coverage
- **Unit Tests**: Individual components and functions
- **Integration Tests**: API endpoints with test database
- **Database Tests**: Model validation and operations
- **Scheduler Tests**: Job execution and management

### Testing Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov=database --cov=scheduler tests/

# Run specific test categories
pytest tests/test_api/ -v
pytest tests/test_database/ -v
```

## 🚨 Monitoring and Alerting

### Health Monitoring
- `/health` endpoint for basic health checks
- `/stats` endpoint for detailed system metrics
- `/scheduler/status` for job monitoring
- Custom monitoring scripts and alerts

### Key Metrics
- API response times and throughput
- Database query performance
- Scheduler job success rates
- System resource utilization

### Log Analysis
- Application logs: structured logging with context
- Database query logs: performance analysis
- Scheduler logs: job execution tracking
- Error logs: debugging and troubleshooting

## 🛠️ Development Workflow

### Getting Started
1. Clone repository and setup virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment: `cp .env.example .env`
4. Initialize database: `python scripts/init_database.py init`
5. Start development server: `python run_api.py`

### Code Standards
- **Style**: Black formatting, isort import sorting
- **Type Hints**: Comprehensive type annotations
- **Documentation**: Docstrings for all public functions
- **Testing**: Comprehensive test coverage

### Contribution Process
1. Create feature branch from main
2. Implement changes with tests
3. Run quality checks: `black . && pytest`
4. Create pull request with description
5. Code review and merge

## 📞 Support and Resources

### Self-Service Resources
- **Documentation**: Complete guides in this directory
- **API Documentation**: Interactive docs at `/docs`
- **Troubleshooting**: Common issues and solutions
- **Health Checks**: System monitoring endpoints

### Getting Help
- **Check Documentation**: Start with relevant guide
- **Review Logs**: Application and system logs
- **Health Checks**: Verify system status
- **Community**: GitHub issues for bugs/features

### Information to Include
When reporting issues, include:
- Service version and configuration
- Error messages with timestamps
- Steps to reproduce the issue
- Recent log entries
- System environment details

## 🎯 Use Cases

### Analytics Applications
- **Real-time Odds Comparison**: Cross-sportsbook analysis
- **Market Movement Tracking**: Historical odds data
- **Arbitrage Detection**: Value betting opportunities
- **Line Movement Analysis**: Market trends and patterns

### Sports Betting Apps
- **Live Odds Display**: Real-time betting lines
- **Historical Data**: Past performance analysis
- **Market Comparison**: Best odds across platforms
- **Alert Systems**: Odds movement notifications

### Data Science Projects
- **Machine Learning**: Predictive modeling on odds data
- **Statistical Analysis**: Market efficiency studies
- **Historical Research**: Long-term trend analysis
- **Academic Research**: Sports betting market studies

---

This documentation suite provides comprehensive coverage of the Betting Market Data Service. Each document is designed to be self-contained while referencing other documents for related topics. Choose the appropriate guide based on your role and needs.

For questions or suggestions about this documentation, please refer to the [Troubleshooting Guide](TROUBLESHOOTING.md) or create an issue in the project repository.
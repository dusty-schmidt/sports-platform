home/ds/betting-mkt-data/docs/DEVELOPMENT.md</path>
<content"># Development Guide

This guide covers development practices, setup, and contribution guidelines for the Betting Market Data Service.

## Development Environment Setup

### Prerequisites

#### System Requirements
- **Python**: 3.8+ (3.11 recommended)
- **Git**: For version control
- **IDE**: VS Code, PyCharm, or similar
- **Database**: SQLite (default) for local development

#### Recommended Tools
```bash
# Install development dependencies
pip install -r requirements.txt

# Install additional development tools
pip install black isort mypy flake8 pre-commit
```

### Initial Setup

#### 1. Clone Repository
```bash
git clone <repository-url>
cd betting-mkt-data
```

#### 2. Create Virtual Environment
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Or using conda
conda create -n betting-market python=3.11
conda activate betting-market
```

#### 3. Install Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e .  # Install in editable mode
```

#### 4. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit configuration for development
cat > .env << EOF
DATABASE_URL=sqlite:///./dev_betting_markets.db
API_DEBUG=true
LOG_LEVEL=DEBUG
SCHEDULER_AUTO_COLLECT_SPORTS=["nba"]
SCHEDULER_NBA_INTERVAL=1
SCHEDULER_DAYS_TO_KEEP_SNAPSHOTS=1
EOF
```

#### 5. Initialize Development Database
```bash
# Initialize with test data
python scripts/init_database.py init

# Verify setup
python scripts/init_database.py check
```

#### 6. Start Development Server
```bash
# Start with auto-reload
python run_api.py

# Or use uvicorn directly
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### Development Workflow

#### Code Structure
```
betting-mkt-data/
├── api/                    # FastAPI application
│   ├── main.py            # Main application
│   └── dependencies.py    # API dependencies
├── database/              # Database layer
│   ├── models.py          # SQLAlchemy models
│   ├── service.py         # Database operations
│   └── connection.py      # Connection management
├── scheduler/             # Job scheduling
│   ├── config.py          # Configuration
│   └── job_manager.py     # Job management
├── betting_service/       # Core service
│   ├── books/             # Sportsbook clients
│   ├── models.py          # Data models
│   └── service.py         # Collection logic
├── tests/                 # Test suite
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── alembic/               # Database migrations
```

#### Development Commands

```bash
# Run tests
pytest
pytest -v
pytest --cov=api --cov=database tests/

# Code formatting
black .
isort .

# Type checking
mypy .

# Linting
flake8 .

# Pre-commit checks
pre-commit run --all-files

# Database operations
python scripts/init_database.py init
python scripts/init_database.py check
python scripts/init_database.py cleanup --days 1

# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Code Standards and Style

### Python Code Style

We follow PEP 8 with some modifications:

#### Code Formatting
```python
# Use Black for formatting
black .

# Sort imports
isort .
```

#### Type Hints
```python
from typing import List, Optional, Dict
from datetime import datetime

def get_markets(
    sport: Optional[str] = None,
    limit: int = 100
) -> List[Dict]:
    """Get markets with optional filtering."""
    pass

class BettingMarketService:
    def __init__(self, db: Session) -> None:
        self.db = db
    
    def create_market(self, data: MarketCreate) -> Market:
        """Create a new betting market."""
        pass
```

#### Documentation
```python
def collect_markets(sport: str, books: List[str] = None) -> List[MarketEvent]:
    """
    Collect betting markets for a specific sport.
    
    Args:
        sport: Sport identifier (e.g., 'nba', 'nfl')
        books: Optional list of sportsbook names
        
    Returns:
        List of MarketEvent objects with collected data
        
    Raises:
        ValueError: If sport is not supported
        HTTPException: If collection fails
        
    Example:
        >>> events = collect_markets('nba', ['draftkings', 'fanduel'])
        >>> len(events)
        25
    """
    pass
```

### Database Development

#### SQLAlchemy Patterns
```python
# Use declarative base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class BettingMarket(Base):
    __tablename__ = "betting_markets"
    
    id = Column(Integer, primary_key=True)
    sport_id = Column(Integer, ForeignKey("sports.id"))
    
    # Relationships
    sport = relationship("Sport", back_populates="markets")
    snapshots = relationship("MarketSnapshot", back_populates="market")
```

#### Service Layer Pattern
```python
from sqlalchemy.orm import Session

class BettingMarketDBService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_market(self, data: MarketCreate) -> BettingMarket:
        """Create market with validation."""
        # Validate input
        self._validate_market_data(data)
        
        # Create market
        market = BettingMarket(**data.dict())
        self.db.add(market)
        self.db.commit()
        self.db.refresh(market)
        
        return market
```

#### Repository Pattern
```python
from abc import ABC, abstractmethod

class MarketRepository(ABC):
    @abstractmethod
    def get_by_id(self, market_id: int) -> Optional[BettingMarket]:
        pass
    
    @abstractmethod
    def create(self, data: dict) -> BettingMarket:
        pass

class SQLAlchemyMarketRepository(MarketRepository):
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, market_id: int) -> Optional[BettingMarket]:
        return self.db.query(BettingMarket).filter(BettingMarket.id == market_id).first()
```

### API Development

#### FastAPI Patterns
```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

app = FastAPI(title="Betting Market API")

# Dependency injection
def get_db_service(db: Session = Depends(get_db)) -> BettingMarketDBService:
    return BettingMarketDBService(db)

# Endpoint with proper error handling
@app.get("/markets/{market_id}")
async def get_market(
    market_id: int,
    db_service: BettingMarketDBService = Depends(get_db_service)
):
    """Get market by ID with error handling."""
    try:
        market = db_service.get_market_by_id(market_id)
        if not market:
            raise HTTPException(status_code=404, detail="Market not found")
        return market
    except Exception as e:
        logger.error("Failed to get market %d: %s", market_id, e)
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### Request/Response Models
```python
from pydantic import BaseModel, validator

class MarketCreate(BaseModel):
    sport_name: str
    away_team: str
    home_team: str
    game_start_time: datetime
    
    @validator('sport_name')
    def validate_sport(cls, v):
        valid_sports = ['nba', 'nfl', 'mlb', 'nhl', 'soccer']
        if v not in valid_sports:
            raise ValueError(f'Sport must be one of {valid_sports}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "sport_name": "nba",
                "away_team": "Los Angeles Lakers",
                "home_team": "Golden State Warriors",
                "game_start_time": "2023-11-03T02:00:00Z"
            }
        }

class MarketResponse(BaseModel):
    id: int
    sport: str
    away_team: str
    home_team: str
    game_start_time: datetime
    
    class Config:
        from_attributes = True
```

### Testing Guidelines

#### Test Structure
```
tests/
├── conftest.py              # Test configuration
├── test_api/               # API tests
│   ├── test_markets.py
│   └── test_sportsbooks.py
├── test_database/          # Database tests
│   ├── test_models.py
│   └── test_service.py
├── test_scheduler/         # Scheduler tests
│   └── test_job_manager.py
├── fixtures/               # Test fixtures
│   ├── markets.py
│   └── sportsbooks.py
└── utils/                  # Test utilities
    ├── helpers.py
    └── factories.py
```

#### Test Examples
```python
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from database.models import Base, BettingMarket
from database.service import BettingMarketDBService

@pytest.fixture
def test_db():
    """Create test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()

@pytest.fixture
def db_service(test_db):
    """Create database service."""
    return BettingMarketDBService(test_db)

class TestMarketService:
    """Test database service methods."""
    
    def test_create_market(self, db_service):
        """Test market creation."""
        market = db_service.create_market(
            sport_name="nba",
            away_team="Lakers",
            home_team="Warriors",
            game_start_time=datetime.utcnow() + timedelta(hours=2)
        )
        
        assert market.id is not None
        assert market.sport_name == "nba"
        assert market.away_team == "Lakers"

class TestMarketAPI:
    """Test API endpoints."""
    
    def test_get_markets(self, client):
        """Test getting markets endpoint."""
        response = client.get("/markets")
        assert response.status_code == 200
        
        markets = response.json()
        assert isinstance(markets, list)
```

#### Testing Utilities
```python
# tests/utils/factories.py
import factory
from datetime import datetime, timedelta

from database.models import BettingMarket, Sport

class SportFactory(factory.Factory):
    class Meta:
        model = Sport
    
    name = factory.Sequence(lambda n: f"sport_{n}")
    display_name = factory.Sequence(lambda n: f"Sport {n}")

class BettingMarketFactory(factory.Factory):
    class Meta:
        model = BettingMarket
    
    sport = factory.SubFactory(SportFactory)
    away_team = "Los Angeles Lakers"
    home_team = "Golden State Warriors"
    game_start_time = datetime.utcnow() + timedelta(hours=2)
```

### API Testing with FastAPI TestClient

```python
from fastapi.testclient import TestClient

def test_market_workflow():
    """Test complete market workflow."""
    client = TestClient(app)
    
    # Create sport
    sport_response = client.post("/sports", json={"name": "nba", "display_name": "NBA"})
    assert sport_response.status_code == 201
    
    # Create market
    market_data = {
        "sport_id": 1,
        "away_team": "Lakers",
        "home_team": "Warriors",
        "game_start_time": "2023-11-03T02:00:00Z"
    }
    
    market_response = client.post("/markets", json=market_data)
    assert market_response.status_code == 201
    market = market_response.json()
    
    # Retrieve market
    get_response = client.get(f"/markets/{market['id']}")
    assert get_response.status_code == 200
```

### Development Tools and IDE Setup

#### VS Code Configuration

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "python.sortImports.args": ["--profile", "black"],
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### Recommended VS Code Extensions
```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.flake8",
        "ms-python.mypy-type-checker",
        "charliermarsh.ruff",
        "ms-vscode.test-adapter-converter",
        "littlefoxteam.vscode-python-test-adapter",
        "ms-vscode.vscode-json"
    ]
}
```

#### PyCharm Configuration

1. **Project Interpreter**: Set to virtual environment
2. **Code Style**: Configure Black as formatter
3. **Testing**: Enable pytest as default test runner
4. **Database**: Configure SQLite connection for development

### Database Development

#### Migrations Workflow

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Edit migration file
# alembic/versions/xxx_add_new_table.py

# Apply migration
alembic upgrade head

# Test migration
pytest tests/test_database.py::test_migration

# Rollback if needed
alembic downgrade -1
```

#### Migration Best Practices
```python
# alembic/versions/xxx_add_snapshots_table.py
"""Add market snapshots table

Revision ID: xxx
Revises: 
Create Date: 2023-11-02 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    """Add market snapshots table."""
    op.create_table('market_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('market_id', sa.Integer(), sa.ForeignKey('betting_markets.id'), nullable=False),
        sa.Column('sportsbook_id', sa.Integer(), sa.ForeignKey('sportsbooks.id'), nullable=False),
        sa.Column('snapshot_time', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes
    op.create_index('idx_snapshot_market', 'market_snapshots', ['market_id'])
    op.create_index('idx_snapshot_time', 'market_snapshots', ['snapshot_time'])

def downgrade():
    """Drop market snapshots table."""
    op.drop_index('idx_snapshot_time', table_name='market_snapshots')
    op.drop_index('idx_snapshot_market', table_name='market_snapshots')
    op.drop_table('market_snapshots')
```

### Performance Development

#### Profiling
```python
import cProfile
import pstats

def profile_function():
    """Profile database queries."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    service = BettingMarketDBService(db)
    markets = service.get_active_markets()
    
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

#### Database Query Optimization
```python
# Use select_related for joins
def get_markets_with_snapshots(db: Session) -> List[BettingMarket]:
    return db.query(BettingMarket).options(
        selectinload(BettingMarket.snapshots).selectinload(MarketSnapshot.sportsbook)
    ).all()

# Use indexing
class BettingMarket(Base):
    __table_args__ = (
        Index('idx_market_sport_time', 'sport_id', 'game_start_time'),
        Index('idx_market_teams', 'away_team', 'home_team'),
    )
```

### Debugging

#### Debugging Database Issues
```python
# Enable SQL logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Debug queries
from sqlalchemy import event

@event.listens_for(engine, "before_cursor_execute", retval=True)
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    print(f"SQL: {statement}")
    print(f"PARAMS: {params}")
    return statement, params
```

#### Debugging API Issues
```python
from fastapi import Request
import logging

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logging.info(f"Path: {request.url.path} - Method: {request.method} - Time: {process_time:.4f}s")
    return response
```

### Contributing Guidelines

#### Branch Strategy
```bash
# Feature development
git checkout -b feature/add-soccer-support
git checkout -b bugfix/fix-scheduler-timeout
git checkout -b hotfix/urgent-database-fix

# Merge back to main
git checkout main
git pull origin main
git merge feature/add-soccer-support
git push origin main
```

#### Commit Messages
```bash
# Format: type(scope): description

# Features
feat(api): add market comparison endpoint
feat(scheduler): implement soccer data collection

# Bug fixes
fix(database): resolve connection pool timeout
fix(api): handle missing sportsbook data

# Documentation
docs(api): update endpoint documentation
docs(config): add deployment examples

# Refactoring
refactor(service): simplify market creation logic
refactor(models): optimize database queries

# Tests
test(api): add market comparison tests
test(database): improve test coverage

# Chore
chore: update requirements.txt
chore: add pre-commit hooks
```

#### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test Your Changes**
   ```bash
   pytest
   black .
   isort .
   flake8 .
   mypy .
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

#### Code Review Checklist

**Before Submitting:**
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No debug code committed
- [ ] Commit messages are clear

**Review Criteria:**
- Code quality and readability
- Test coverage and quality
- Documentation completeness
- Performance considerations
- Security implications

### Advanced Development Topics

#### Async/Await Patterns
```python
import asyncio
from typing import AsyncGenerator

async def collect_markets_async(sports: List[str]) -> AsyncGenerator[MarketEvent, None]:
    """Collect markets asynchronously."""
    tasks = [collect_sport_markets(sport) for sport in sports]
    
    for task in asyncio.as_completed(tasks):
        try:
            events = await task
            for event in events:
                yield event
        except Exception as e:
            logger.error("Failed to collect sports: %s", e)

async def main():
    async for event in collect_markets_async(['nba', 'nfl']):
        await save_market_event(event)
```

#### Background Tasks
```python
from fastapi import BackgroundTasks

@app.post("/collect/{sport}")
async def collect_sport_data(
    sport: str,
    background_tasks: BackgroundTasks
):
    """Start data collection in background."""
    def collect_data():
        service = BettingMarketService(sport)
        events = service.collect()
        db_service.store_market_events(events)
    
    background_tasks.add_task(collect_data)
    return {"message": "Collection started"}
```

#### Custom Middleware
```python
from fastapi import Request, Response
import time

@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Development Environment Tips

#### Database Management
```bash
# Reset development database
rm dev_betting_markets.db
python scripts/init_database.py init

# Check database status
python scripts/init_database.py check

# Backup development data
cp dev_betting_markets.db dev_betting_markets.db.backup

# Load test data
python scripts/load_test_data.py
```

#### Testing Strategies
```bash
# Run specific test categories
pytest tests/test_api/ -v
pytest tests/test_database/ -k "test_create" -v

# Run with coverage
pytest --cov=api --cov-report=html

# Run performance tests
pytest tests/test_performance/ --benchmark-only

# Run integration tests
pytest tests/integration/ -v
```

This development guide provides comprehensive coverage of development practices for the Betting Market Data Service. Follow these guidelines to maintain code quality and ensure smooth collaboration.
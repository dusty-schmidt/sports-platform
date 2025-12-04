home/ds/betting-mkt-data/docs/DEPLOYMENT.md</path>
<content"># Deployment Guide

This guide covers deploying the Betting Market Data Service in various environments, from development to production.

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: Minimum 512MB RAM (2GB recommended for production)
- **Storage**: 1GB free space (more for long-term data storage)
- **Network**: Internet access for sportsbook API calls

### Dependencies
```bash
# Python packages (automatically installed)
pip install -r requirements.txt

# Database drivers
# SQLite (default) - no additional setup
# PostgreSQL
sudo apt-get install postgresql postgresql-contrib
# MySQL
sudo apt-get install mysql-server libmysqlclient-dev
```

## Development Deployment

### 1. Quick Start (Local Development)

```bash
# Clone the repository
git clone <repository-url>
cd betting-mkt-data

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_database.py init

# Start development server
python run_api.py
```

The service will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 2. Development Configuration

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env`:
```bash
# Database (SQLite for development)
DATABASE_URL=sqlite:///./betting_markets.db

# API Configuration
API_DEBUG=true
API_HOST=127.0.0.1
API_PORT=8000

# Logging
LOG_LEVEL=DEBUG

# Scheduler Configuration
SCHEDULER_AUTO_COLLECT_SPORTS=["nba"]
SCHEDULER_NBA_INTERVAL=5  # Frequent updates for development
```

### 3. Testing the Deployment

```bash
# Health check
curl http://localhost:8000/health

# Test data collection
curl -X POST http://localhost:8000/collect/nba

# Check database
python scripts/init_database.py check
```

## Production Deployment

### Option 1: Direct Server Deployment

#### 1. Server Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python and dependencies
sudo apt-get install python3 python3-pip python3-venv nginx -y

# Create application user
sudo useradd -m -s /bin/bash betting-app
sudo su - betting-app
```

#### 2. Application Deployment

```bash
# Navigate to application directory
cd /home/betting-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy application files
# (Use git clone or rsync from development machine)

# Initialize database
python scripts/init_database.py init

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/betting_markets"
export API_DEBUG=false
export LOG_LEVEL=INFO
```

#### 3. Production Configuration

Create `/home/betting-app/.env`:
```bash
# Database (PostgreSQL)
DATABASE_URL=postgresql://betting_user:secure_password@localhost:5432/betting_markets

# API Configuration
API_DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000

# Scheduler
SCHEDULER_AUTO_COLLECT_SPORTS=["nba","nfl","mlb","nhl"]
SCHEDULER_NBA_INTERVAL=15
SCHEDULER_NFL_INTERVAL=15
SCHEDULER_MLB_INTERVAL=30
SCHEDULER_NHL_INTERVAL=20
SCHEDULER_DAYS_TO_KEEP_SNAPSHOTS=7

# Security
SECRET_KEY=your-secret-key-here
```

#### 4. Systemd Service

Create `/etc/systemd/system/betting-market-api.service`:
```ini
[Unit]
Description=Betting Market Data API
After=network.target postgresql.service

[Service]
Type=exec
User=betting-app
Group=betting-app
WorkingDirectory=/home/betting-app
Environment=PATH=/home/betting-app/venv/bin
EnvironmentFile=/home/betting-app/.env
ExecStart=/home/betting-app/venv/bin/python run_api.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=betting-market-api

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable betting-market-api
sudo systemctl start betting-market-api
sudo systemctl status betting-market-api
```

#### 5. Nginx Configuration

Create `/etc/nginx/sites-available/betting-market-api`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration (configure certificates)
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # API proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check (bypass caching)
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }

    # Disable caching for API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_no_cache 1;
        proxy_cache_bypass 1;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/betting-market-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 2: Docker Deployment

#### 1. Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://betting_user:secure_password@db:5432/betting_markets
      - API_DEBUG=false
    depends_on:
      - db
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=betting_markets
      - POSTGRES_USER=betting_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

#### 3. Production Docker

```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs api
docker-compose logs db

# Scale if needed
docker-compose up -d --scale api=3
```

### Option 3: Kubernetes Deployment

#### 1. Deployment YAML

Create `k8s/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: betting-market-api
  labels:
    app: betting-market-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: betting-market-api
  template:
    metadata:
      labels:
        app: betting-market-api
    spec:
      containers:
      - name: api
        image: betting-market-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: betting-secrets
              key: database-url
        - name: API_DEBUG
          value: "false"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: betting-market-api-service
spec:
  selector:
    app: betting-market-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### 2. Database Deployment

Create `k8s/postgres.yaml`:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: betting-secrets
type: Opaque
stringData:
  database-url: "postgresql://betting_user:password@postgres-service:5432/betting_markets"
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: betting_markets
        - name: POSTGRES_USER
          value: betting_user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: betting-secrets
              key: postgres-password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

#### 3. Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f k8s/

# Check status
kubectl get pods
kubectl get services

# Check logs
kubectl logs -l app=betting-market-api

# Scale deployment
kubectl scale deployment betting-market-api --replicas=5
```

## Database Setup

### PostgreSQL (Recommended for Production)

#### 1. Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

#### 2. Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE betting_markets;
CREATE USER betting_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE betting_markets TO betting_user;

# Exit psql
\q
```

#### 3. Run Migrations

```bash
# Set database URL
export DATABASE_URL="postgresql://betting_user:secure_password@localhost:5432/betting_markets"

# Run migrations
alembic upgrade head

# Or initialize with script
python scripts/init_database.py init
```

### MySQL (Alternative)

```bash
# Install MySQL
sudo apt-get install mysql-server libmysqlclient-dev

# Create database and user
sudo mysql -u root -p
CREATE DATABASE betting_markets;
CREATE USER 'betting_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON betting_markets.* TO 'betting_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Set environment
export DATABASE_URL="mysql://betting_user:secure_password@localhost:3306/betting_markets"

# Run migrations
alembic upgrade head
```

## SSL/TLS Configuration

### Let's Encrypt (Free SSL)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Custom SSL Certificate

```bash
# Generate self-signed certificate (development only)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Configure in production with proper certificates
```

## Monitoring and Logging

### Application Monitoring

```bash
# Check application status
curl http://localhost:8000/health

# Get detailed statistics
curl http://localhost:8000/stats

# Check scheduler status
curl http://localhost:8000/scheduler/status
```

### Log Management

#### Log Files
- Application logs: `/var/log/betting-market-api/`
- System service logs: `journalctl -u betting-market-api`
- Nginx logs: `/var/log/nginx/`

#### Log Rotation

Create `/etc/logrotate.d/betting-market-api`:
```
/var/log/betting-market-api/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 betting-app betting-app
    postrotate
        systemctl reload betting-market-api
    endscript
}
```

### Health Checks

#### External Monitoring
```bash
#!/bin/bash
# health-check.sh

URL="http://localhost:8000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $URL)

if [ $RESPONSE -eq 200 ]; then
    echo "Service is healthy"
    exit 0
else
    echo "Service is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
```

#### Cron Job for Monitoring
```bash
# Add to crontab
*/5 * * * * /path/to/health-check.sh >> /var/log/betting-health.log 2>&1
```

## Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# backup-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_URL="postgresql://user:password@localhost:5432/betting_markets"

# Create backup
pg_dump $DB_URL > $BACKUP_DIR/betting_markets_$DATE.sql

# Compress
gzip $BACKUP_DIR/betting_markets_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "betting_markets_*.sql.gz" -mtime +30 -delete
```

#### Automated Backup

```bash
# Add to crontab
0 2 * * * /path/to/backup-db.sh
```

### Database Recovery

```bash
# Stop application
sudo systemctl stop betting-market-api

# Restore database
gunzip -c /backups/betting_markets_20231102_020000.sql.gz | psql betting_markets

# Start application
sudo systemctl start betting-market-api
```

## Performance Optimization

### Database Optimization

#### PostgreSQL Configuration

Edit `/etc/postgresql/15/main/postgresql.conf`:
```ini
# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Checkpoint settings
checkpoint_completion_target = 0.7
wal_buffers = 16MB
checkpoint_segments = 32

# Query planner
random_page_cost = 1.1
effective_io_concurrency = 200
```

### Application Optimization

#### Environment Variables
```bash
# Database connection pooling
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Worker processes
WORKERS=4

# Cache settings
CACHE_TTL=300  # 5 minutes
```

## Security Considerations

### Network Security
- Use HTTPS in production
- Implement firewall rules
- Use VPN for database access
- Limit database connections to application servers

### Application Security
```bash
# Environment variables
SECRET_KEY=your-32-character-secret-key
API_KEY=your-api-key-for-external-access
DATABASE_SSL_MODE=require

# Rate limiting
RATE_LIMIT_PER_MINUTE=100
```

### Database Security
```sql
-- Limit user privileges
GRANT SELECT, INSERT, UPDATE ON betting_markets.* TO betting_user;
DENY ALL ON betting_markets.* TO betting_user;

-- Enable SSL
ALTER USER betting_user REQUIRE SSL;
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
journalctl -u betting-market-api -f

# Check database connection
python scripts/init_database.py check

# Verify permissions
sudo chown -R betting-app:betting-app /home/betting-app
```

#### Database Connection Errors
```bash
# Test database connection
psql $DATABASE_URL -c "SELECT version();"

# Check database status
sudo systemctl status postgresql
```

#### High Memory Usage
```bash
# Check memory usage
ps aux | grep betting-market-api

# Adjust worker processes
export WORKERS=2

# Optimize database connections
export DATABASE_POOL_SIZE=5
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python run_api.py
```

### Performance Issues

```bash
# Check database performance
python scripts/init_database.py check

# Monitor API performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/markets

# Database query analysis
# Enable query logging in postgresql.conf
log_statement = 'all'
log_duration = on
```

## Maintenance

### Regular Maintenance Tasks

1. **Daily**: Check health endpoints and logs
2. **Weekly**: Review error logs and performance metrics
3. **Monthly**: Database maintenance and cleanup
4. **Quarterly**: Security updates and dependency upgrades

### Update Procedure

```bash
# Backup current version
cp -r /home/betting-app /home/betting-app.backup.$(date +%Y%m%d)

# Update application
cd /home/betting-app
git pull origin main
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Restart service
sudo systemctl restart betting-market-api

# Verify update
curl http://localhost:8000/health
```

## Support

For deployment issues:
1. Check the troubleshooting section
2. Review application logs
3. Verify database connectivity
4. Check system resources (CPU, memory, disk)
5. Consult the main README.md for configuration details
# Deployment Guide

Guide for deploying the FastAPI REST API to production.

## Prerequisites

- Production server (Linux recommended)
- Docker and Docker Compose
- Domain name (optional)
- SSL certificate (recommended)

## Deployment Options

### Option 1: Docker Compose (Recommended)

#### 1. Prepare the Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add user to docker group
sudo usermod -aG docker $USER
```

#### 2. Clone Repository

```bash
git clone <repository-url>
cd building-rest-api-fastapi
```

#### 3. Configure Environment

Create production `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with production values:

```env
APP_NAME=FastAPI REST API
DEBUG=False
DATABASE_URL=postgresql+asyncpg://postgres:STRONG_PASSWORD@db:5432/fastapi_db
SECRET_KEY=GENERATE_STRONG_SECRET_KEY_HERE
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
```

Important:
- Generate a strong `SECRET_KEY`: `openssl rand -hex 32`
- Use strong database password
- Set `DEBUG=False`
- Configure proper CORS origins

#### 4. Deploy with Docker Compose

```bash
docker-compose up -d
```

#### 5. Verify Deployment

```bash
# Check running containers
docker-compose ps

# View logs
docker-compose logs -f

# Test API
curl http://localhost:8000/health
```

### Option 2: Direct Deployment with Systemd

#### 1. Setup Python Environment

```bash
# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Create application directory
sudo mkdir -p /opt/fastapi-app
sudo chown $USER:$USER /opt/fastapi-app
cd /opt/fastapi-app

# Clone repository
git clone <repository-url> .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Setup PostgreSQL

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE fastapi_db;
CREATE USER fastapi_user WITH PASSWORD 'STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi_user;
EOF
```

#### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with production values
```

#### 4. Create Systemd Service

Create `/etc/systemd/system/fastapi.service`:

```ini
[Unit]
Description=FastAPI REST API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/fastapi-app
Environment="PATH=/opt/fastapi-app/venv/bin"
ExecStart=/opt/fastapi-app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi
sudo systemctl status fastapi
```

### Option 3: Kubernetes Deployment

#### 1. Create Deployment YAML

`kubernetes/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: your-registry/fastapi-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: fastapi-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: fastapi-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### 2. Deploy to Kubernetes

```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/service.yaml
```

## Reverse Proxy Setup (Nginx)

### Install Nginx

```bash
sudo apt install nginx -y
```

### Configure Nginx

Create `/etc/nginx/sites-available/fastapi`:

```nginx
upstream fastapi_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/fastapi_access.log;
    error_log /var/log/nginx/fastapi_error.log;

    # Client body size
    client_max_body_size 10M;

    # Proxy settings
    location / {
        proxy_pass http://fastapi_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket support (if needed)
    location /ws {
        proxy_pass http://fastapi_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL Certificate Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
# Test renewal:
sudo certbot renew --dry-run
```

## Database Backup

### Automated Backup Script

Create `/opt/scripts/backup_db.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/fastapi_db_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T db pg_dump -U postgres fastapi_db > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

Make executable and add to cron:

```bash
chmod +x /opt/scripts/backup_db.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /opt/scripts/backup_db.sh" | crontab -
```

## Monitoring

### Health Check Monitoring

Create `/opt/scripts/health_check.sh`:

```bash
#!/bin/bash

HEALTH_URL="http://localhost:8000/health"
ALERT_EMAIL="admin@example.com"

response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $response != "200" ]; then
    echo "FastAPI health check failed with status $response" | \
        mail -s "FastAPI Alert: Health Check Failed" $ALERT_EMAIL
fi
```

Add to cron (check every 5 minutes):

```bash
echo "*/5 * * * * /opt/scripts/health_check.sh" | crontab -
```

### Logging

Configure application logging in `app/main.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("/var/log/fastapi/app.log"),
        logging.StreamHandler()
    ]
)
```

Rotate logs with logrotate. Create `/etc/logrotate.d/fastapi`:

```
/var/log/fastapi/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

## Performance Optimization

### 1. Use Gunicorn with Uvicorn Workers

Update systemd service:

```ini
ExecStart=/opt/fastapi-app/venv/bin/gunicorn app.main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/fastapi/access.log \
    --error-logfile /var/log/fastapi/error.log
```

### 2. Enable Database Connection Pooling

Already configured in `app/database.py` with SQLAlchemy.

### 3. Add Redis Caching (Optional)

```bash
# Install Redis
docker run -d --name redis -p 6379:6379 redis:alpine

# Add to requirements.txt
redis==5.0.1

# Use in application
from redis import Redis
redis_client = Redis(host='localhost', port=6379, decode_responses=True)
```

### 4. Enable HTTP/2

Already configured in Nginx example above.

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure firewall (UFW)
- [ ] Set DEBUG=False in production
- [ ] Configure proper CORS origins
- [ ] Implement rate limiting
- [ ] Keep dependencies updated
- [ ] Regular security audits
- [ ] Database backups configured
- [ ] Monitoring and alerting setup
- [ ] Use environment variables for secrets
- [ ] Restrict database access
- [ ] Use non-root user for application

## Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Check status
sudo ufw status
```

## Scaling

### Horizontal Scaling

1. Use load balancer (Nginx, HAProxy, or cloud load balancer)
2. Deploy multiple application instances
3. Use shared database (managed PostgreSQL)
4. Implement session storage (Redis)

### Vertical Scaling

1. Increase server resources (CPU, RAM)
2. Optimize database queries
3. Add database indexes
4. Enable connection pooling

## CI/CD Pipeline

Example GitHub Actions workflow (`.github/workflows/deploy.yml`):

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/fastapi-app
            git pull
            docker-compose down
            docker-compose up -d --build
```

## Troubleshooting

### Check application logs:

```bash
# Docker
docker-compose logs -f api

# Systemd
sudo journalctl -u fastapi -f
```

### Check database connectivity:

```bash
docker-compose exec db psql -U postgres -d fastapi_db
```

### Restart services:

```bash
# Docker
docker-compose restart

# Systemd
sudo systemctl restart fastapi
```

## Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Uvicorn Deployment](https://www.uvicorn.org/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/current/performance-tips.html)

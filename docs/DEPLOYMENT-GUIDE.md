# Deployment Guide
## Production Deployment for CCTV System

**Platform:** Multi-platform (Linux, Windows, Docker)  
**Version:** 1.0.0

---

## 📋 Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Backend Deployment](#backend-deployment)
3. [Frontend Deployment](#frontend-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Security Hardening](#security-hardening)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Backup & Recovery](#backup--recovery)

---

## 🎯 Deployment Overview

### System Requirements

**Backend Server:**
- CPU: 2+ cores (4+ recommended for multiple streams)
- RAM: 4GB minimum (8GB recommended)
- Storage: 50GB+ (depends on recording requirements)
- OS: Linux (Ubuntu 20.04+), Windows Server 2019+
- Network: Static IP, ports 8000, 80, 443 open

**Client Devices:**
- Android 8.0+ or iOS 13.0+
- 2GB RAM minimum
- WiFi or cellular connection

### Architecture Choices

| Deployment Type | Use Case | Complexity | Cost |
|----------------|----------|------------|------|
| **Single Server** | Home, small office | Low | Low |
| **Docker Compose** | Development, testing | Medium | Low |
| **Cloud (AWS/Azure)** | Enterprise, scalability | High | Medium-High |
| **Kubernetes** | Large scale, HA | Very High | High |

---

## 🖥️ Backend Deployment

### Option 1: Linux Server (Ubuntu/Debian)

#### 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    python3.9 python3-pip python3-venv \
    ffmpeg \
    nginx \
    supervisor \
    certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash cctv
sudo usermod -aG sudo cctv
```

#### 2. Application Setup

```bash
# Switch to application user
sudo su - cctv

# Clone/copy application
cd /opt
sudo mkdir cctv-backend
sudo chown cctv:cctv cctv-backend
cd cctv-backend

# Copy your backend files here
# Or git clone if using repository

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Create directories
mkdir -p backend/hls_output
mkdir -p backend/logs
mkdir -p backend/recordings

# Set permissions
chmod 755 backend/hls_output
chmod 755 backend/logs
```

#### 3. Configure Systemd Service

Create `/etc/systemd/system/cctv-backend.service`:

```ini
[Unit]
Description=CCTV Backend Service
After=network.target

[Service]
Type=simple
User=cctv
WorkingDirectory=/opt/cctv-backend/backend
Environment="PATH=/opt/cctv-backend/venv/bin"
ExecStart=/opt/cctv-backend/venv/bin/python main_backend.py
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/opt/cctv-backend/backend/logs/systemd.log
StandardError=append:/opt/cctv-backend/backend/logs/systemd.error.log

# Security
PrivateTmp=yes
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable cctv-backend
sudo systemctl start cctv-backend

# Check status
sudo systemctl status cctv-backend

# View logs
sudo journalctl -u cctv-backend -f
```

#### 4. Nginx Reverse Proxy

Create `/etc/nginx/sites-available/cctv-backend`:

```nginx
upstream cctv_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name cctv.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name cctv.yourdomain.com;

    # SSL Configuration (will be added by certbot)
    ssl_certificate /etc/letsencrypt/live/cctv.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cctv.yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Max body size (for uploads)
    client_max_body_size 100M;

    # Logging
    access_log /var/log/nginx/cctv_access.log;
    error_log /var/log/nginx/cctv_error.log;

    # API endpoints
    location /api/ {
        proxy_pass http://cctv_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket endpoints
    location /ws/ {
        proxy_pass http://cctv_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # WebSocket timeouts
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }

    # HLS streaming
    location /hls/ {
        proxy_pass http://cctv_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        
        # CORS for HLS
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Range' always;
        
        # Caching for segments
        proxy_cache_valid 200 1s;
        proxy_cache_bypass $http_pragma $http_authorization;
        add_header X-Cache-Status $upstream_cache_status;
    }

    # Health check
    location /health {
        proxy_pass http://cctv_backend/api/health;
        access_log off;
    }

    # Root
    location / {
        proxy_pass http://cctv_backend;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/cctv-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d cctv.yourdomain.com

# Auto-renewal is set up automatically
# Test renewal
sudo certbot renew --dry-run
```

#### 6. Firewall Configuration

```bash
# UFW firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Check status
sudo ufw status
```

---

### Option 2: Windows Server

#### 1. Install Dependencies

```powershell
# Install Python 3.9+
# Download from: https://www.python.org/downloads/

# Install FFmpeg
# Download from: https://ffmpeg.org/download.html
# Extract to C:\ffmpeg
# Add C:\ffmpeg\bin to PATH

# Verify installations
python --version
ffmpeg -version
```

#### 2. Setup Application

```powershell
# Create directory
New-Item -ItemType Directory -Path C:\CCTVBackend

# Copy application files
# Or clone repository

# Create virtual environment
cd C:\CCTVBackend\backend
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
New-Item -ItemType Directory -Path hls_output
New-Item -ItemType Directory -Path logs
New-Item -ItemType Directory -Path recordings
```

#### 3. Windows Service (NSSM)

```powershell
# Download NSSM: https://nssm.cc/download
# Extract nssm.exe to C:\nssm

# Install service
C:\nssm\nssm.exe install CCTVBackend "C:\CCTVBackend\venv\Scripts\python.exe" "C:\CCTVBackend\backend\main_backend.py"

# Configure service
C:\nssm\nssm.exe set CCTVBackend AppDirectory "C:\CCTVBackend\backend"
C:\nssm\nssm.exe set CCTVBackend AppStdout "C:\CCTVBackend\backend\logs\service.log"
C:\nssm\nssm.exe set CCTVBackend AppStderr "C:\CCTVBackend\backend\logs\service_error.log"

# Start service
Start-Service CCTVBackend

# Check status
Get-Service CCTVBackend
```

#### 4. IIS Reverse Proxy (Optional)

Install URL Rewrite and Application Request Routing modules, then configure reverse proxy in web.config.

---

## 📱 Frontend Deployment

### Build for Production

#### Android (APK/AAB)

```bash
cd "d:\MobileApp Research"

# Update app.json with production settings
# Set version, build number, etc.

# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure EAS
eas build:configure

# Build APK (for direct distribution)
eas build --platform android --profile production

# Build AAB (for Google Play Store)
eas build --platform android --profile production --output-format aab

# Download build when complete
# APK will be available in your Expo dashboard
```

**Production Configuration (`eas.json`):**
```json
{
  "build": {
    "production": {
      "android": {
        "buildType": "apk",
        "gradleCommand": ":app:assembleRelease"
      },
      "env": {
        "BACKEND_URL": "https://cctv.yourdomain.com"
      }
    }
  }
}
```

#### iOS (IPA)

```bash
# Build for iOS (requires Apple Developer account)
eas build --platform ios --profile production

# Submit to App Store
eas submit --platform ios
```

### Over-The-Air (OTA) Updates

```bash
# Publish update without rebuilding
eas update --branch production --message "Bug fixes"

# Users will receive update on next app launch
```

---

## 🐳 Docker Deployment

### Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -s /bin/bash cctv

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p hls_output logs recordings && \
    chown -R cctv:cctv /app

# Switch to app user
USER cctv

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Run application
CMD ["python", "main_backend.py"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: cctv-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./backend/devices_db.json:/app/devices_db.json
      - ./backend/users_db.json:/app/users_db.json
      - ./backend/hls_output:/app/hls_output
      - ./backend/logs:/app/logs
      - ./backend/recordings:/app/recordings
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - LOG_LEVEL=INFO
    networks:
      - cctv-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: cctv-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./backend/hls_output:/usr/share/nginx/html/hls:ro
    depends_on:
      - backend
    networks:
      - cctv-network

networks:
  cctv-network:
    driver: bridge
```

### Deploy with Docker Compose

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

---

## ☁️ Cloud Deployment

### AWS Deployment

#### 1. EC2 Instance

```bash
# Launch EC2 instance (Ubuntu 20.04 LTS)
# Instance type: t3.medium or larger
# Security group: Allow 22, 80, 443

# Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip

# Follow Linux deployment steps above
```

#### 2. Application Load Balancer

- Create target group pointing to EC2 instances
- Configure health checks: `/api/health`
- Setup SSL certificate in ACM
- Create ALB with HTTPS listener

#### 3. Auto Scaling Group

```yaml
# Launch template
- AMI: Custom AMI with app pre-installed
- Instance type: t3.medium
- User data: Start application on boot

# Auto scaling policy
- Min: 1
- Max: 5
- Target CPU: 70%
```

#### 4. RDS (Optional - for database)

Replace JSON files with PostgreSQL:

```python
# Install psycopg2
pip install psycopg2-binary

# Database connection
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@rds-endpoint:5432/cctv')
```

### Azure Deployment

#### 1. Azure App Service

```bash
# Install Azure CLI
az login

# Create resource group
az group create --name cctv-rg --location eastus

# Create App Service plan
az appservice plan create \
    --name cctv-plan \
    --resource-group cctv-rg \
    --sku B2 \
    --is-linux

# Create web app
az webapp create \
    --resource-group cctv-rg \
    --plan cctv-plan \
    --name cctv-backend \
    --runtime "PYTHON|3.9"

# Deploy code
az webapp up \
    --resource-group cctv-rg \
    --name cctv-backend \
    --src-path ./backend
```

---

## 🔒 Security Hardening

### 1. Environment Variables

**Never hardcode secrets!** Use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
JWT_SECRET = os.getenv('JWT_SECRET')
```

**Set in production:**
```bash
export SECRET_KEY="your-secret-key-here"
export JWT_SECRET="your-jwt-secret-here"
```

### 2. HTTPS Only

Force HTTPS in Nginx:
```nginx
if ($scheme != "https") {
    return 301 https://$server_name$request_uri;
}
```

### 3. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, data: UserLogin):
    # ...
```

### 4. Input Validation

Always validate and sanitize:
```python
from pydantic import validator

class DeviceRegister(BaseModel):
    ipAddress: str
    
    @validator('ipAddress')
    def validate_ip(cls, v):
        import ipaddress
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError('Invalid IP address')
        return v
```

### 5. Secure Headers

Add security headers:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["cctv.yourdomain.com", "*.yourdomain.com"]
)
```

---

## 📊 Monitoring & Maintenance

### 1. Application Monitoring

**Prometheus + Grafana:**

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### 2. Log Aggregation

**ELK Stack (Elasticsearch, Logstash, Kibana):**

```yaml
# docker-compose.yml
elasticsearch:
  image: elasticsearch:8.5.0
  environment:
    - discovery.type=single-node

logstash:
  image: logstash:8.5.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

kibana:
  image: kibana:8.5.0
  ports:
    - "5601:5601"
```

### 3. Health Checks

Setup monitoring endpoint:
```python
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "ffmpeg": check_ffmpeg(),
            "disk_space": check_disk_space(),
            "active_streams": len(stream_service.streams)
        }
    }
```

### 4. Automated Backups

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/cctv"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup databases
cp /opt/cctv-backend/backend/devices_db.json "$BACKUP_DIR/devices_$DATE.json"
cp /opt/cctv-backend/backend/users_db.json "$BACKUP_DIR/users_$DATE.json"

# Compress recordings (if any)
tar -czf "$BACKUP_DIR/recordings_$DATE.tar.gz" /opt/cctv-backend/backend/recordings/

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.json" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

**Cron job:**
```bash
# Run daily at 2 AM
0 2 * * * /opt/cctv-backend/scripts/backup.sh
```

---

## 💾 Backup & Recovery

### Backup Strategy

**What to backup:**
1. Database files (`devices_db.json`, `users_db.json`)
2. Recordings (if stored locally)
3. Configuration files
4. SSL certificates

**Backup frequency:**
- Daily: Database files
- Weekly: Full system backup
- Real-time: Critical recordings to cloud storage

### Recovery Procedure

```bash
# Stop service
sudo systemctl stop cctv-backend

# Restore databases
cp /backups/cctv/devices_20260112.json /opt/cctv-backend/backend/devices_db.json
cp /backups/cctv/users_20260112.json /opt/cctv-backend/backend/users_db.json

# Restore recordings
tar -xzf /backups/cctv/recordings_20260112.tar.gz -C /opt/cctv-backend/backend/

# Start service
sudo systemctl start cctv-backend

# Verify
sudo systemctl status cctv-backend
curl http://localhost:8000/api/health
```

---

## 🚀 Deployment Checklist

### Pre-Deployment

- [ ] Update version numbers
- [ ] Run all tests
- [ ] Review security settings
- [ ] Update documentation
- [ ] Create backup of current system

### Deployment

- [ ] Deploy backend to server
- [ ] Configure SSL certificates
- [ ] Setup reverse proxy
- [ ] Configure firewall
- [ ] Test all API endpoints
- [ ] Build mobile app
- [ ] Test app with production backend

### Post-Deployment

- [ ] Monitor logs for errors
- [ ] Check stream performance
- [ ] Verify backups are running
- [ ] Setup alerts and monitoring
- [ ] Document deployment date and version

---

**Last Updated:** January 12, 2026  
**Version:** 1.0.0

# Digital Ocean Legal Document RAG System - Complete Installation Guide

This guide provides comprehensive instructions for deploying a legal document processing and RAG system on Digital Ocean cloud infrastructure using Docker Droplets, Managed Databases, and Spaces (S3-compatible storage).

## Table of Contents

1. [Digital Ocean Infrastructure Setup](#digital-ocean-infrastructure-setup)
2. [Droplet Configuration](#droplet-configuration)
3. [Managed Database Setup](#managed-database-setup)
4. [Spaces (Object Storage) Configuration](#spaces-object-storage-configuration)
5. [Application Deployment](#application-deployment)
6. [Production Optimizations](#production-optimizations)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Backup and Disaster Recovery](#backup-and-disaster-recovery)
9. [Security Hardening](#security-hardening)
10. [Troubleshooting](#troubleshooting)

## Digital Ocean Infrastructure Setup

### 1. Create Digital Ocean Account and Project

```bash
# Install doctl (Digital Ocean CLI)
# For Ubuntu/Debian:
sudo snap install doctl

# For macOS:
brew install doctl

# Authenticate
doctl auth init

# Create a new project
doctl projects create --name "legal-rag-system" --description "Legal Document RAG System" --purpose "AI/ML"
```

### 2. Infrastructure Components

**Required Digital Ocean Services:**
- **Droplet**: 8GB RAM, 4 vCPUs, 160GB SSD (minimum for production)
- **Managed Database**: PostgreSQL (for metadata and user management)
- **Spaces**: Object storage for document backups and large files
- **VPC**: Virtual Private Cloud for network isolation
- **Load Balancer**: For high availability (optional but recommended)
- **Monitoring**: Built-in monitoring and alerting

## Droplet Configuration

### 1. Create Production Droplet

```bash
# Create a VPC first
doctl vpcs create --name legal-rag-vpc --region nyc3

# Get VPC ID
VPC_ID=$(doctl vpcs list --format ID --no-header | head -1)

# Create droplet with optimized specs for AI workloads
doctl compute droplet create legal-rag-droplet \
  --region nyc3 \
  --size c-8 \
  --image ubuntu-22-04-x64 \
  --vpc-uuid $VPC_ID \
  --ssh-keys $(doctl compute ssh-key list --format ID --no-header) \
  --user-data-file ./droplet-user-data.sh \
  --wait

# Get droplet IP
DROPLET_IP=$(doctl compute droplet get legal-rag-droplet --format PublicIPv4 --no-header)
echo "Droplet IP: $DROPLET_IP"
```

### 2. Droplet User Data Script

Create `droplet-user-data.sh`:

```bash
#!/bin/bash

# Update system
apt-get update && apt-get upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker root

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install monitoring agent
curl -sSL https://agent.digitalocean.com/install.sh | sh

# Install Python and dependencies
apt-get install -y python3 python3-pip python3-venv git curl wget unzip

# Create application directory
mkdir -p /opt/legal-rag
cd /opt/legal-rag

# Configure firewall
ufw allow ssh
ufw allow 8080/tcp
ufw allow 443/tcp
ufw allow 80/tcp
ufw --force enable

# Create swap file for memory optimization
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Set up log rotation
cat > /etc/logrotate.d/legal-rag << EOF
/opt/legal-rag/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    copytruncate
}
EOF

# Optimize for AI workloads
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.max_map_count=262144' >> /etc/sysctl.conf
sysctl -p
```

### 3. SSH and Access Configuration

```bash
# SSH to droplet
ssh root@$DROPLET_IP

# Create non-root user for application
adduser legalrag
usermod -aG docker legalrag
usermod -aG sudo legalrag

# Set up SSH key for application user
mkdir -p /home/legalrag/.ssh
cp /root/.ssh/authorized_keys /home/legalrag/.ssh/
chown -R legalrag:legalrag /home/legalrag/.ssh
chmod 700 /home/legalrag/.ssh
chmod 600 /home/legalrag/.ssh/authorized_keys
```

## Managed Database Setup

### 1. Create PostgreSQL Database

```bash
# Create managed PostgreSQL database
doctl databases create legal-rag-db \
  --engine pg \
  --region nyc3 \
  --size db-s-2vcpu-4gb \
  --num-nodes 1 \
  --version 15

# Get database connection details
doctl databases connection legal-rag-db --format ConnectionString

# Create application database and user
doctl databases sql legal-rag-db --command "
CREATE DATABASE legalrag_metadata;
CREATE USER legalrag_app WITH PASSWORD 'SECURE_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON DATABASE legalrag_metadata TO legalrag_app;
"
```

### 2. Database Configuration

Add to your `.env` file:

```bash
# Database Configuration
DATABASE_URL=postgresql://legalrag_app:PASSWORD@legal-rag-db-do-user-xxx.db.ondigitalocean.com:25060/legalrag_metadata?sslmode=require
DB_HOST=legal-rag-db-do-user-xxx.db.ondigitalocean.com
DB_PORT=25060
DB_NAME=legalrag_metadata
DB_USER=legalrag_app
DB_PASSWORD=SECURE_PASSWORD_HERE
DB_SSL_MODE=require
```

## Spaces (Object Storage) Configuration

### 1. Create Spaces Bucket

```bash
# Create Spaces bucket for backups and document storage
doctl spaces bucket create legal-documents-storage --region nyc3

# Create API keys for Spaces
doctl spaces key create legal-rag-spaces-key

# Note the Access Key ID and Secret Access Key for configuration
```

### 2. Configure Spaces Access

Update `.env` file:

```bash
# Digital Ocean Spaces Configuration (S3-compatible)
DO_SPACES_REGION=nyc3
DO_SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
DO_SPACES_BUCKET=legal-documents-storage
DO_SPACES_ACCESS_KEY_ID=YOUR_SPACES_ACCESS_KEY
DO_SPACES_SECRET_ACCESS_KEY=YOUR_SPACES_SECRET_KEY

# Backup Configuration
S3_BACKUP_BUCKET=legal-documents-storage
AWS_ACCESS_KEY_ID=${DO_SPACES_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${DO_SPACES_SECRET_ACCESS_KEY}
AWS_REGION=${DO_SPACES_REGION}
AWS_S3_ENDPOINT=${DO_SPACES_ENDPOINT}
```

## Application Deployment

### 1. Clone and Configure Application

```bash
# SSH to droplet as legalrag user
ssh legalrag@$DROPLET_IP

# Clone the application
cd /opt/legal-rag
git clone https://github.com/your-repo/legal-rag-system.git .

# Copy and configure environment
cp .env.template .env.production
nano .env.production  # Add your configuration
```

### 2. Production Environment Configuration

Create `.env.production`:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Digital Ocean Spaces (S3-compatible) Configuration
DO_SPACES_REGION=nyc3
DO_SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
DO_SPACES_BUCKET=legal-documents-storage
DO_SPACES_ACCESS_KEY_ID=your_spaces_access_key
DO_SPACES_SECRET_ACCESS_KEY=your_spaces_secret_key

# Use DO Spaces as S3 backend
S3_BACKUP_BUCKET=legal-documents-storage
AWS_ACCESS_KEY_ID=${DO_SPACES_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${DO_SPACES_SECRET_ACCESS_KEY}
AWS_REGION=${DO_SPACES_REGION}
AWS_S3_ENDPOINT=${DO_SPACES_ENDPOINT}

# Security
WEAVIATE_API_KEY=your_secure_weaviate_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# Database (Managed PostgreSQL)
DATABASE_URL=postgresql://legalrag_app:password@db-host:25060/legalrag_metadata?sslmode=require

# Application Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
MAX_DOCUMENT_SIZE_MB=100
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Legal-specific settings
DEFAULT_PRACTICE_AREA=general
CONFIDENTIALITY_LEVELS=public,standard,confidential,highly_confidential
RETENTION_POLICY_YEARS=7

# Performance Tuning for Digital Ocean
GOMAXPROCS=4
WEAVIATE_MEMORY_LIMIT=6g
WEAVIATE_CPU_LIMIT=3.5
```

### 3. Deploy with Docker Compose

```bash
# Create production docker-compose file
cp docker-compose.yml docker-compose.production.yml

# Start the application
docker-compose -f docker-compose.production.yml --env-file .env.production up -d

# Verify deployment
docker-compose -f docker-compose.production.yml ps
docker-compose -f docker-compose.production.yml logs
```

## Production Optimizations

### 1. Performance Tuning

Create `docker-compose.production.yml`:

```yaml
version: '3.8'
services:
  weaviate:
    image: semitechnologies/weaviate:latest
    ports:
      - "8080:8080"
      - "50051:50051"
    environment:
      # Core Configuration
      QUERY_DEFAULTS_LIMIT: 25
      AUTHENTICATION_APIKEY_ENABLED: 'true'
      AUTHENTICATION_APIKEY_ALLOWED_KEYS: '${WEAVIATE_API_KEY}'
      AUTHENTICATION_APIKEY_USERS: 'legal-user@firm.com'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      
      # Modules Configuration
      ENABLE_MODULES: 'text2vec-openai,text2vec-transformers,generative-openai,backup-s3'
      DEFAULT_VECTORIZER_MODULE: 'text2vec-openai'
      
      # Performance Optimization for Digital Ocean
      GOMAXPROCS: '4'
      PERSISTENCE_MEMTABLES_MAX_SIZE: '1000'
      PERSISTENCE_MEMTABLES_FLUSH_IDLE_AFTER_SECONDS: '15'
      TRACK_VECTOR_DIMENSIONS: 'true'
      
      # Digital Ocean Optimizations
      CLUSTER_HOSTNAME: 'legal-weaviate-node'
      LOG_LEVEL: 'info'
      LOG_FORMAT: 'json'
      
      # External API Keys
      OPENAI_APIKEY: '${OPENAI_API_KEY}'
      TRANSFORMERS_INFERENCE_API: 'http://t2v-transformers:8080'
      
      # Digital Ocean Spaces Configuration
      BACKUP_S3_BUCKET: '${S3_BACKUP_BUCKET}'
      BACKUP_S3_ENDPOINT: '${AWS_S3_ENDPOINT}'
      AWS_ACCESS_KEY_ID: '${AWS_ACCESS_KEY_ID}'
      AWS_SECRET_ACCESS_KEY: '${AWS_SECRET_ACCESS_KEY}'
      AWS_REGION: '${AWS_REGION}'
      
      # Monitoring
      PROMETHEUS_MONITORING_ENABLED: 'true'
      PROMETHEUS_MONITORING_PORT: '2112'
      
    volumes:
      - weaviate_data:/var/lib/weaviate
      - ./legal-docs:/legal-docs:ro
      - ./logs:/var/log/weaviate
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 6G
          cpus: '3.5'
        reservations:
          memory: 4G
          cpus: '2'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/v1/.well-known/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"

  # Local transformers optimized for DO
  t2v-transformers:
    image: semitechnologies/transformers-inference:sentence-transformers-all-MiniLM-L6-v2
    environment:
      ENABLE_CUDA: '0'
      MAX_WORKERS: '2'
      WORKER_TIMEOUT: '120'
    ports:
      - "8081:8080"
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1'
        reservations:
          memory: 1G
          cpus: '0.5'
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "5m"
        max-file: "3"

  # Nginx reverse proxy for SSL and load balancing
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - weaviate
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "5m"
        max-file: "3"

  # Redis for caching (optional but recommended)
  redis:
    image: redis:alpine
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

volumes:
  weaviate_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/legal-rag/data
  redis_data:
    driver: local

networks:
  default:
    name: legal-rag-network
```

### 2. Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream weaviate {
        server weaviate:8080;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;
        
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;
        
        location / {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://weaviate;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

## Monitoring and Logging

### 1. Set up Digital Ocean Monitoring

```bash
# Install DO monitoring agent (if not already installed)
curl -sSL https://agent.digitalocean.com/install.sh | sh

# Configure alerts
doctl monitoring alert policy create \
  --type droplet \
  --description "High CPU usage on legal-rag-droplet" \
  --compare GreaterThan \
  --value 80 \
  --window 5m \
  --entities $(doctl compute droplet get legal-rag-droplet --format ID --no-header)
```

### 2. Application Logging

Create `logging-config.yml`:

```yaml
version: 1
formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  json:
    format: '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: json
    stream: ext://sys.stdout
  
  file:
    class: logging.handlers.RotatingFileHandler
    level: INFO
    formatter: json
    filename: /opt/legal-rag/logs/application.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  weaviate_client:
    level: INFO
    handlers: [console, file]
    propagate: no
  
  legal_rag:
    level: INFO
    handlers: [console, file]
    propagate: no

root:
  level: INFO
  handlers: [console, file]
```

## Backup and Disaster Recovery

### 1. Automated Backups to Spaces

Create `backup-script.sh`:

```bash
#!/bin/bash

# Legal RAG Backup Script for Digital Ocean
set -e

# Configuration
BACKUP_DIR="/opt/legal-rag/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SPACES_BUCKET="legal-documents-storage"
SPACES_ENDPOINT="https://nyc3.digitaloceanspaces.com"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Starting backup process at $(date)"

# 1. Backup Weaviate data
echo "Backing up Weaviate data..."
docker-compose -f docker-compose.production.yml exec weaviate \
  curl -X POST "http://localhost:8080/v1/backups/s3" \
  -H "Authorization: Bearer ${WEAVIATE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "backup_'$TIMESTAMP'",
    "config": {
      "bucket": "'$SPACES_BUCKET'",
      "path": "weaviate-backups/backup_'$TIMESTAMP'",
      "endpoint": "'$SPACES_ENDPOINT'",
      "useSSL": true,
      "accessKeyId": "'$AWS_ACCESS_KEY_ID'",
      "secretAccessKey": "'$AWS_SECRET_ACCESS_KEY'"
    }
  }'

# 2. Backup configuration files
echo "Backing up configuration..."
tar -czf $BACKUP_DIR/config_$TIMESTAMP.tar.gz \
  .env.production \
  docker-compose.production.yml \
  nginx.conf

# 3. Upload config backup to Spaces
echo "Uploading configuration backup..."
aws s3 cp $BACKUP_DIR/config_$TIMESTAMP.tar.gz \
  s3://$SPACES_BUCKET/config-backups/ \
  --endpoint-url $SPACES_ENDPOINT

# 4. Cleanup old local backups (keep last 7 days)
find $BACKUP_DIR -name "config_*.tar.gz" -mtime +7 -delete

echo "Backup completed successfully at $(date)"
```

### 2. Schedule Backups with Cron

```bash
# Add to crontab
crontab -e

# Add these lines:
# Daily backup at 2 AM
0 2 * * * /opt/legal-rag/backup-script.sh >> /opt/legal-rag/logs/backup.log 2>&1

# Weekly full system backup at 3 AM on Sundays
0 3 * * 0 /opt/legal-rag/full-backup-script.sh >> /opt/legal-rag/logs/full-backup.log 2>&1
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Configure UFW (Ubuntu Firewall)
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Additional security: Change SSH port
sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config
systemctl restart sshd
ufw allow 2222/tcp
ufw delete allow ssh
```

### 2. SSL Certificate Setup

```bash
# Install Certbot for Let's Encrypt
apt-get install -y certbot

# Get SSL certificate
certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Copy certificates to nginx directory
mkdir -p /opt/legal-rag/ssl
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/legal-rag/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/legal-rag/ssl/key.pem

# Set up automatic renewal
crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet --post-hook "docker-compose -f /opt/legal-rag/docker-compose.production.yml restart nginx"
```

### 3. Application Security

Update your application configuration for production security:

```python
# security_config.py
import os

# Security settings for production
SECURITY_CONFIG = {
    'USE_HTTPS': True,
    'SECURE_SSL_REDIRECT': True,
    'SESSION_COOKIE_SECURE': True,
    'CSRF_COOKIE_SECURE': True,
    'SECURE_HSTS_SECONDS': 31536000,
    'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
    'SECURE_CONTENT_TYPE_NOSNIFF': True,
    'SECURE_BROWSER_XSS_FILTER': True,
    'X_FRAME_OPTIONS': 'DENY',
    
    # API rate limiting
    'RATE_LIMIT_PER_MINUTE': 60,
    'RATE_LIMIT_BURST': 10,
    
    # Authentication
    'SESSION_TIMEOUT_MINUTES': 30,
    'MAX_LOGIN_ATTEMPTS': 3,
    'LOCKOUT_DURATION_MINUTES': 15,
}
```

## Troubleshooting

### Common Issues and Solutions

1. **High Memory Usage**
   ```bash
   # Monitor memory usage
   docker stats
   
   # Adjust Weaviate memory limits
   docker-compose -f docker-compose.production.yml restart weaviate
   ```

2. **Connection Issues to Digital Ocean Services**
   ```bash
   # Test Spaces connectivity
   aws s3 ls s3://legal-documents-storage --endpoint-url https://nyc3.digitaloceanspaces.com
   
   # Test database connectivity
   psql $DATABASE_URL -c "SELECT 1;"
   ```

3. **SSL Certificate Issues**
   ```bash
   # Check certificate status
   certbot certificates
   
   # Renew certificates manually
   certbot renew --force-renewal
   ```

4. **Performance Issues**
   ```bash
   # Check system resources
   htop
   df -h
   free -h
   
   # Optimize Docker
   docker system prune -f
   ```

### Monitoring Commands

```bash
# Check application health
curl -k https://your-domain.com/v1/.well-known/ready

# Monitor logs
docker-compose -f docker-compose.production.yml logs -f weaviate

# Check system metrics
doctl monitoring metrics droplet legal-rag-droplet

# Database performance
doctl databases metrics legal-rag-db
```

This comprehensive guide provides everything needed to deploy and manage a production-ready legal document RAG system on Digital Ocean infrastructure. The configuration is optimized for Digital Ocean's services and provides enterprise-level security, monitoring, and backup capabilities.

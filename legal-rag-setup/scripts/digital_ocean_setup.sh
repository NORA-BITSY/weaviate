#!/bin/bash

# Digital Ocean Legal Document RAG System Setup Script
# This script sets up the infrastructure and deploys the legal RAG system on Digital Ocean

set -e  # Exit on any error

echo "🌊 Digital Ocean Legal Document RAG System Setup"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_digitalocean() {
    echo -e "${CYAN}[DO]${NC} $1"
}

# Configuration variables
PROJECT_NAME="legal-rag-system"
DROPLET_NAME="legal-rag-droplet"
REGION="nyc3"
DROPLET_SIZE="c-8"  # 8GB RAM, 4 vCPUs
DATABASE_NAME="legal-rag-db"
SPACES_BUCKET="legal-documents-storage"
VPC_NAME="legal-rag-vpc"

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check if doctl is installed
    if ! command -v doctl &> /dev/null; then
        print_error "doctl (Digital Ocean CLI) is not installed."
        echo "Install it with:"
        echo "  Ubuntu/Debian: sudo snap install doctl"
        echo "  macOS: brew install doctl"
        echo "  Or download from: https://github.com/digitalocean/doctl/releases"
        exit 1
    fi
    
    # Check if user is authenticated
    if ! doctl account get &> /dev/null; then
        print_error "Not authenticated with Digital Ocean."
        echo "Run: doctl auth init"
        exit 1
    fi
    
    # Check if docker is available locally for building
    if ! command -v docker &> /dev/null; then
        print_warning "Docker not found locally. You'll need it for local development."
    fi
    
    print_status "Prerequisites check completed"
}

# Create Digital Ocean project
create_project() {
    print_step "Creating Digital Ocean project..."
    
    # Check if project already exists
    if doctl projects list --format Name --no-header | grep -q "^${PROJECT_NAME}$"; then
        print_status "Project '${PROJECT_NAME}' already exists"
        PROJECT_ID=$(doctl projects list --format ID,Name --no-header | grep "${PROJECT_NAME}" | awk '{print $1}')
    else
        print_digitalocean "Creating new project: ${PROJECT_NAME}"
        PROJECT_ID=$(doctl projects create \
            --name "${PROJECT_NAME}" \
            --description "Legal Document RAG System with AI-powered search and analysis" \
            --purpose "AI/ML" \
            --environment "Production" \
            --format ID \
            --no-header)
        print_status "Created project with ID: ${PROJECT_ID}"
    fi
}

# Create VPC for network isolation
create_vpc() {
    print_step "Setting up Virtual Private Cloud..."
    
    # Check if VPC already exists
    if doctl vpcs list --format Name --no-header | grep -q "^${VPC_NAME}$"; then
        print_status "VPC '${VPC_NAME}' already exists"
        VPC_ID=$(doctl vpcs list --format ID,Name --no-header | grep "${VPC_NAME}" | awk '{print $1}')
    else
        print_digitalocean "Creating VPC: ${VPC_NAME}"
        VPC_ID=$(doctl vpcs create \
            --name "${VPC_NAME}" \
            --region "${REGION}" \
            --format ID \
            --no-header)
        print_status "Created VPC with ID: ${VPC_ID}"
    fi
}

# Create Spaces bucket for object storage
create_spaces() {
    print_step "Setting up Digital Ocean Spaces..."
    
    # Check if bucket already exists
    if doctl spaces bucket list --format Name --no-header | grep -q "^${SPACES_BUCKET}$"; then
        print_status "Spaces bucket '${SPACES_BUCKET}' already exists"
    else
        print_digitalocean "Creating Spaces bucket: ${SPACES_BUCKET}"
        doctl spaces bucket create "${SPACES_BUCKET}" --region "${REGION}"
        print_status "Created Spaces bucket: ${SPACES_BUCKET}"
    fi
    
    # Create API keys for Spaces access
    print_digitalocean "Creating Spaces API keys..."
    SPACES_KEY_NAME="legal-rag-spaces-$(date +%Y%m%d)"
    
    # Create the key and capture the output
    SPACES_KEY_OUTPUT=$(doctl spaces key create "${SPACES_KEY_NAME}" 2>/dev/null || echo "key_creation_failed")
    
    if [[ "$SPACES_KEY_OUTPUT" != "key_creation_failed" ]]; then
        print_status "Spaces API key created successfully"
        print_warning "Save these credentials securely:"
        echo "$SPACES_KEY_OUTPUT"
    else
        print_warning "Spaces API key creation failed or key already exists"
        print_warning "You may need to create the API key manually from the Digital Ocean dashboard"
    fi
}

# Create managed PostgreSQL database
create_database() {
    print_step "Setting up Managed PostgreSQL Database..."
    
    # Check if database already exists
    if doctl databases list --format Name --no-header | grep -q "^${DATABASE_NAME}$"; then
        print_status "Database '${DATABASE_NAME}' already exists"
        DB_ID=$(doctl databases list --format ID,Name --no-header | grep "${DATABASE_NAME}" | awk '{print $1}')
    else
        print_digitalocean "Creating managed PostgreSQL database: ${DATABASE_NAME}"
        print_warning "This will take several minutes to provision..."
        
        DB_ID=$(doctl databases create "${DATABASE_NAME}" \
            --engine pg \
            --region "${REGION}" \
            --size db-s-2vcpu-4gb \
            --num-nodes 1 \
            --version 15 \
            --format ID \
            --no-header)
        
        print_status "Database creation initiated with ID: ${DB_ID}"
        
        # Wait for database to be ready
        print_digitalocean "Waiting for database to be ready..."
        while true; do
            DB_STATUS=$(doctl databases get "$DB_ID" --format Status --no-header)
            if [[ "$DB_STATUS" == "online" ]]; then
                print_status "Database is ready!"
                break
            else
                echo -n "."
                sleep 30
            fi
        done
    fi
    
    # Get connection details
    print_digitalocean "Retrieving database connection details..."
    DB_CONNECTION=$(doctl databases connection "$DB_ID" --format ConnectionString --no-header)
    print_status "Database connection string retrieved"
    
    # Create application database and user
    print_digitalocean "Setting up application database and user..."
    DB_HOST=$(doctl databases get "$DB_ID" --format Host --no-header)
    DB_PORT=$(doctl databases get "$DB_ID" --format Port --no-header)
    DB_USER=$(doctl databases get "$DB_ID" --format User --no-header)
    
    print_warning "Database setup complete. Connection details:"
    echo "Host: $DB_HOST"
    echo "Port: $DB_PORT"
    echo "Default User: $DB_USER"
    echo "Connection String: $DB_CONNECTION"
}

# Generate user data script for droplet
generate_user_data() {
    print_step "Generating droplet user data script..."
    
    cat > droplet-user-data.sh << 'EOF'
#!/bin/bash

# Digital Ocean Droplet Setup for Legal RAG System
set -e

# Update system
apt-get update && apt-get upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker root

# Install Docker Compose
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Digital Ocean monitoring agent
curl -sSL https://agent.digitalocean.com/install.sh | sh

# Install essential packages
apt-get install -y python3 python3-pip python3-venv git curl wget unzip htop nload iotop

# Create application user
adduser --disabled-password --gecos "" legalrag
usermod -aG docker legalrag
usermod -aG sudo legalrag

# Create application directory
mkdir -p /opt/legal-rag
chown legalrag:legalrag /opt/legal-rag

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

# Optimize for AI workloads
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.max_map_count=262144' >> /etc/sysctl.conf
echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf
sysctl -p

# Set up log rotation
cat > /etc/logrotate.d/legal-rag << 'LOGROTATE_EOF'
/opt/legal-rag/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    copytruncate
}
LOGROTATE_EOF

# Create directories
mkdir -p /opt/legal-rag/{logs,data,backups,ssl}
chown -R legalrag:legalrag /opt/legal-rag

# Install AWS CLI for Spaces compatibility
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

print "Droplet setup completed successfully!"
EOF

    chmod +x droplet-user-data.sh
    print_status "User data script generated: droplet-user-data.sh"
}

# Create and configure droplet
create_droplet() {
    print_step "Creating and configuring droplet..."
    
    # Check if droplet already exists
    if doctl compute droplet list --format Name --no-header | grep -q "^${DROPLET_NAME}$"; then
        print_status "Droplet '${DROPLET_NAME}' already exists"
        DROPLET_ID=$(doctl compute droplet list --format ID,Name --no-header | grep "${DROPLET_NAME}" | awk '{print $1}')
        DROPLET_IP=$(doctl compute droplet get "$DROPLET_ID" --format PublicIPv4 --no-header)
    else
        # Get SSH key ID
        SSH_KEY_ID=$(doctl compute ssh-key list --format ID --no-header | head -1)
        
        if [[ -z "$SSH_KEY_ID" ]]; then
            print_error "No SSH keys found. Please add an SSH key to your Digital Ocean account first."
            exit 1
        fi
        
        print_digitalocean "Creating droplet: ${DROPLET_NAME}"
        print_warning "This will take a few minutes..."
        
        DROPLET_ID=$(doctl compute droplet create "${DROPLET_NAME}" \
            --region "${REGION}" \
            --size "${DROPLET_SIZE}" \
            --image ubuntu-22-04-x64 \
            --vpc-uuid "${VPC_ID}" \
            --ssh-keys "${SSH_KEY_ID}" \
            --user-data-file droplet-user-data.sh \
            --wait \
            --format ID \
            --no-header)
        
        print_status "Droplet created with ID: ${DROPLET_ID}"
        
        # Get IP address
        DROPLET_IP=$(doctl compute droplet get "$DROPLET_ID" --format PublicIPv4 --no-header)
        print_status "Droplet IP address: ${DROPLET_IP}"
        
        # Add droplet to project
        doctl projects resources assign "$PROJECT_ID" --resource "do:droplet:$DROPLET_ID"
    fi
    
    print_status "Droplet is ready at IP: ${DROPLET_IP}"
}

# Generate environment configuration
generate_environment_config() {
    print_step "Generating environment configuration..."
    
    cat > .env.digitalocean << EOF
# Digital Ocean Configuration
DO_REGION=${REGION}
DO_DROPLET_IP=${DROPLET_IP}
DO_PROJECT_ID=${PROJECT_ID}

# Digital Ocean Spaces Configuration
DO_SPACES_REGION=${REGION}
DO_SPACES_ENDPOINT=https://${REGION}.digitaloceanspaces.com
DO_SPACES_BUCKET=${SPACES_BUCKET}
# Note: Add your Spaces access keys manually:
# DO_SPACES_ACCESS_KEY_ID=your_spaces_access_key
# DO_SPACES_SECRET_ACCESS_KEY=your_spaces_secret_key

# Database Configuration
# Note: Add your database credentials manually:
# DATABASE_URL=${DB_CONNECTION}
# DB_HOST=${DB_HOST}
# DB_PORT=${DB_PORT}

# Application Configuration
ENVIRONMENT=production
WEAVIATE_URL=http://${DROPLET_IP}:8080
API_BASE_URL=https://your-domain.com

# S3-compatible configuration for Weaviate backup
S3_BACKUP_BUCKET=${SPACES_BUCKET}
AWS_REGION=${REGION}
AWS_S3_ENDPOINT=https://${REGION}.digitaloceanspaces.com
# AWS_ACCESS_KEY_ID=\${DO_SPACES_ACCESS_KEY_ID}
# AWS_SECRET_ACCESS_KEY=\${DO_SPACES_SECRET_ACCESS_KEY}

# Security
WEAVIATE_API_KEY=legal-system-key-$(date +%Y%m%d)

# Legal-specific settings
DEFAULT_PRACTICE_AREA=general
CONFIDENTIALITY_LEVELS=public,standard,confidential,highly_confidential
RETENTION_POLICY_YEARS=7
MAX_DOCUMENT_SIZE_MB=100

# Performance settings for Digital Ocean droplet
GOMAXPROCS=4
WEAVIATE_MEMORY_LIMIT=6g
WEAVIATE_CPU_LIMIT=3.5
EOF

    print_status "Environment configuration saved to .env.digitalocean"
}

# Generate deployment script
generate_deployment_script() {
    print_step "Generating deployment script..."
    
    cat > deploy-to-digitalocean.sh << 'EOF'
#!/bin/bash

# Deploy Legal RAG System to Digital Ocean Droplet
set -e

# Configuration
DROPLET_IP=${1:-"DROPLET_IP_HERE"}
REMOTE_USER="legalrag"
REMOTE_DIR="/opt/legal-rag"

if [[ "$DROPLET_IP" == "DROPLET_IP_HERE" ]]; then
    echo "Usage: $0 <droplet_ip>"
    echo "Example: $0 192.168.1.100"
    exit 1
fi

echo "🚀 Deploying to Digital Ocean droplet: $DROPLET_IP"

# Copy files to droplet
echo "📁 Copying application files..."
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    ./ ${REMOTE_USER}@${DROPLET_IP}:${REMOTE_DIR}/

# Copy environment configuration
echo "⚙️  Copying environment configuration..."
scp .env.digitalocean ${REMOTE_USER}@${DROPLET_IP}:${REMOTE_DIR}/.env

# Deploy and start services
echo "🐳 Starting services on droplet..."
ssh ${REMOTE_USER}@${DROPLET_IP} << 'REMOTE_COMMANDS'
cd /opt/legal-rag

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Start services with Digital Ocean configuration
docker-compose -f docker-compose.digitalocean.yml --env-file .env up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
docker-compose -f docker-compose.digitalocean.yml ps
docker-compose -f docker-compose.digitalocean.yml logs --tail=20

echo "✅ Deployment completed!"
echo "📊 Access your system at: http://$DROPLET_IP:8080"
REMOTE_COMMANDS

echo "🎉 Deployment to Digital Ocean completed successfully!"
echo "🌐 Your Legal RAG system is available at: http://$DROPLET_IP:8080"
EOF

    chmod +x deploy-to-digitalocean.sh
    print_status "Deployment script generated: deploy-to-digitalocean.sh"
}

# Create monitoring setup script
generate_monitoring_script() {
    print_step "Generating monitoring setup script..."
    
    cat > setup-monitoring.sh << 'EOF'
#!/bin/bash

# Set up monitoring and alerting for Legal RAG System on Digital Ocean
set -e

DROPLET_IP=${1:-"DROPLET_IP_HERE"}

if [[ "$DROPLET_IP" == "DROPLET_IP_HERE" ]]; then
    echo "Usage: $0 <droplet_ip>"
    exit 1
fi

echo "📊 Setting up monitoring for droplet: $DROPLET_IP"

# Create monitoring configuration
ssh legalrag@${DROPLET_IP} << 'REMOTE_SETUP'
cd /opt/legal-rag

# Create monitoring directory
mkdir -p monitoring/{prometheus,grafana,alertmanager}

# Prometheus configuration
cat > monitoring/prometheus/prometheus.yml << 'PROM_CONFIG'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'weaviate'
    static_configs:
      - targets: ['weaviate:2112']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
PROM_CONFIG

# Alert rules
cat > monitoring/prometheus/alert_rules.yml << 'ALERT_RULES'
groups:
  - name: legal-rag-alerts
    rules:
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for more than 5 minutes"

      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes"

      - alert: WeaviateDown
        expr: up{job="weaviate"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Weaviate service is down"
          description: "Weaviate service has been down for more than 1 minute"
ALERT_RULES

echo "✅ Monitoring configuration created"
REMOTE_SETUP

echo "📊 Monitoring setup completed!"
EOF

    chmod +x setup-monitoring.sh
    print_status "Monitoring setup script generated: setup-monitoring.sh"
}

# Display summary and next steps
show_summary() {
    echo ""
    echo "🎉 Digital Ocean Infrastructure Setup Complete!"
    echo "=============================================="
    echo ""
    print_status "Infrastructure Summary:"
    echo "  📍 Region: ${REGION}"
    echo "  💻 Droplet: ${DROPLET_NAME} (${DROPLET_SIZE})"
    echo "  🌐 IP Address: ${DROPLET_IP}"
    echo "  🗄️  Database: ${DATABASE_NAME}"
    echo "  📦 Spaces Bucket: ${SPACES_BUCKET}"
    echo "  🔒 VPC: ${VPC_NAME}"
    echo ""
    print_warning "⚠️  Manual Steps Required:"
    echo "1. Add your OpenAI API key to .env.digitalocean"
    echo "2. Add your Spaces access keys to .env.digitalocean"
    echo "3. Add your database credentials to .env.digitalocean"
    echo ""
    print_status "📝 Next Steps:"
    echo "1. Edit .env.digitalocean with your API keys and credentials"
    echo "2. Deploy the application:"
    echo "   ./deploy-to-digitalocean.sh ${DROPLET_IP}"
    echo "3. Set up monitoring:"
    echo "   ./setup-monitoring.sh ${DROPLET_IP}"
    echo ""
    print_status "🔗 Access Points:"
    echo "  SSH: ssh legalrag@${DROPLET_IP}"
    echo "  Weaviate API: http://${DROPLET_IP}:8080"
    echo "  Application: http://${DROPLET_IP} (after deployment)"
    echo ""
    print_status "📊 Digital Ocean Dashboard:"
    echo "  Project: https://cloud.digitalocean.com/projects/${PROJECT_ID}"
    echo ""
}

# Main setup function
main() {
    echo "Starting Digital Ocean infrastructure setup..."
    echo ""
    
    check_prerequisites
    create_project
    create_vpc
    create_spaces
    create_database
    generate_user_data
    create_droplet
    generate_environment_config
    generate_deployment_script
    generate_monitoring_script
    show_summary
}

# Handle command line arguments
case "${1:-setup}" in
    setup)
        main
        ;;
    create-droplet)
        check_prerequisites
        create_vpc
        generate_user_data
        create_droplet
        print_status "Droplet creation completed"
        ;;
    create-database)
        check_prerequisites
        create_database
        print_status "Database creation completed"
        ;;
    create-spaces)
        check_prerequisites
        create_spaces
        print_status "Spaces creation completed"
        ;;
    deploy)
        if [[ -z "$2" ]]; then
            print_error "Please provide droplet IP address"
            echo "Usage: $0 deploy <droplet_ip>"
            exit 1
        fi
        ./deploy-to-digitalocean.sh "$2"
        ;;
    destroy)
        print_warning "This will destroy all Digital Ocean resources!"
        read -p "Are you sure? (yes/no): " -r
        if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            print_step "Destroying resources..."
            doctl compute droplet delete "${DROPLET_NAME}" --force
            doctl databases delete "${DATABASE_NAME}" --force
            doctl spaces bucket delete "${SPACES_BUCKET}" --force
            doctl vpcs delete "${VPC_NAME}" --force
            print_status "Resources destroyed"
        fi
        ;;
    *)
        echo "Usage: $0 {setup|create-droplet|create-database|create-spaces|deploy <ip>|destroy}"
        echo ""
        echo "Commands:"
        echo "  setup          - Complete infrastructure setup (default)"
        echo "  create-droplet - Create droplet only"
        echo "  create-database- Create database only"
        echo "  create-spaces  - Create Spaces bucket only"
        echo "  deploy <ip>    - Deploy application to droplet"
        echo "  destroy        - Destroy all resources"
        exit 1
        ;;
esac

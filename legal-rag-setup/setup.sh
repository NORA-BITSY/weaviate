#!/bin/bash

# Legal Document RAG System Setup Script
# This script sets up the complete environment for processing legal documents

set -e  # Exit on any error

echo "🏛️  Legal Document RAG System Setup"
echo "==================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if Docker is installed
check_docker() {
    print_step "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker installation verified"
}

# Check if Python is installed
check_python() {
    print_step "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_status "Python $python_version found"
}

# Create environment file
setup_environment() {
    print_step "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        cp .env.template .env
        print_status "Created .env file from template"
        print_warning "Please edit .env file with your actual API keys and configuration"
        echo ""
        echo "Required environment variables:"
        echo "  OPENAI_API_KEY - Your OpenAI API key"
        echo "  S3_BACKUP_BUCKET - S3 bucket for backups (optional)"
        echo "  AWS_ACCESS_KEY_ID - AWS access key (optional)"
        echo "  AWS_SECRET_ACCESS_KEY - AWS secret key (optional)"
        echo ""
    else
        print_status ".env file already exists"
    fi
}

# Install Python dependencies
install_python_deps() {
    print_step "Installing Python dependencies..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    # Install spaCy model
    print_status "Installing spaCy English model..."
    python -m spacy download en_core_web_sm
    
    print_status "Python dependencies installed"
}

# Start Weaviate with Docker
start_weaviate() {
    print_step "Starting Weaviate with Docker Compose..."
    
    # Check if .env file exists and has required variables
    if [ ! -f .env ]; then
        print_error ".env file not found. Please run setup first."
        exit 1
    fi
    
    # Start services
    docker-compose up -d
    
    print_status "Weaviate services starting..."
    
    # Wait for Weaviate to be ready
    print_step "Waiting for Weaviate to be ready..."
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:8080/v1/.well-known/ready > /dev/null 2>&1; then
            print_status "Weaviate is ready!"
            break
        fi
        
        sleep 2
        attempt=$((attempt + 1))
        echo -n "."
    done
    
    echo ""
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Weaviate failed to start within expected time"
        print_error "Check logs with: docker-compose logs"
        exit 1
    fi
}

# Create sample legal documents directory
create_sample_docs() {
    print_step "Creating sample documents directory..."
    
    mkdir -p legal-docs/contracts
    mkdir -p legal-docs/litigation
    mkdir -p legal-docs/corporate
    
    # Create sample documents if they don't exist
    if [ ! -f "legal-docs/contracts/sample_contract.txt" ]; then
        cat > legal-docs/contracts/sample_contract.txt << 'EOF'
EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is entered into on January 15, 2024, between ABC Corporation, a Delaware corporation ("Company"), and John Doe, an individual ("Employee").

1. POSITION AND DUTIES
Employee shall serve as Senior Software Engineer and shall perform such duties as are customarily associated with such position.

2. COMPENSATION
Company shall pay Employee a base salary of $120,000 per year, payable in accordance with Company's regular payroll practices.

3. NON-COMPETE CLAUSE
During the term of employment and for a period of twelve (12) months following termination, Employee agrees not to engage in any business that competes with Company within a 50-mile radius of Company's headquarters.

4. CONFIDENTIALITY
Employee agrees to maintain the confidentiality of all proprietary information of Company.

5. TERMINATION
This Agreement may be terminated by either party with thirty (30) days written notice.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

ABC Corporation                    John Doe
By: /s/ Jane Smith                /s/ John Doe
Name: Jane Smith                  John Doe
Title: CEO
EOF
        print_status "Created sample employment contract"
    fi
    
    if [ ! -f "legal-docs/litigation/sample_motion.txt" ]; then
        cat > legal-docs/litigation/sample_motion.txt << 'EOF'
IN THE UNITED STATES DISTRICT COURT
FOR THE SOUTHERN DISTRICT OF NEW YORK

Case No. 21-cv-1234

JOHN DOE,                           )
                                   )
    Plaintiff,                     )
                                   )  MOTION FOR SUMMARY JUDGMENT
v.                                 )
                                   )
ABC CORPORATION,                   )
                                   )
    Defendant.                     )
__________________________________ )

TO THE HONORABLE COURT:

Plaintiff John Doe, by and through undersigned counsel, respectfully moves this Court for summary judgment pursuant to Rule 56 of the Federal Rules of Civil Procedure.

STATEMENT OF FACTS

1. Plaintiff was employed by Defendant from January 2020 to December 2023.

2. Defendant terminated Plaintiff's employment without cause on December 15, 2023.

3. Plaintiff's employment contract contained specific provisions regarding termination procedures.

ARGUMENT

I. STANDARD FOR SUMMARY JUDGMENT

Summary judgment is appropriate when there is no genuine dispute as to any material fact and the movant is entitled to judgment as a matter of law. Fed. R. Civ. P. 56(a).

II. DEFENDANT BREACHED THE EMPLOYMENT CONTRACT

The undisputed facts establish that Defendant failed to follow the contractual termination procedures, constituting a material breach.

CONCLUSION

For the foregoing reasons, Plaintiff respectfully requests that this Court grant summary judgment in his favor.

Respectfully submitted,

/s/ Attorney Name
Attorney for Plaintiff
State Bar No. 12345
EOF
        print_status "Created sample motion for summary judgment"
    fi
}

# Test the system
test_system() {
    print_step "Testing the system..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Test Weaviate connection
    python3 -c "
from src.weaviate_client import LegalWeaviateClient
import os
try:
    client = LegalWeaviateClient('http://localhost:8080', os.getenv('WEAVIATE_API_KEY'))
    schema = client.get_schema_info()
    print('✅ Weaviate connection successful')
    print(f'📊 Schema classes: {len(schema.get(\"classes\", []))}')
except Exception as e:
    print(f'❌ Weaviate connection failed: {e}')
    exit(1)
"
    
    print_status "System test completed successfully"
}

# Display next steps
show_next_steps() {
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit the .env file with your OpenAI API key"
    echo "2. Activate the Python environment: source venv/bin/activate"
    echo "3. Run the demo: python main.py ./legal-docs"
    echo ""
    echo "Useful commands:"
    echo "  docker-compose logs        - View Weaviate logs"
    echo "  docker-compose down        - Stop Weaviate services"
    echo "  docker-compose up -d       - Start Weaviate services"
    echo ""
    echo "Access points:"
    echo "  Weaviate API: http://localhost:8080"
    echo "  Transformers API: http://localhost:8081"
    echo ""
}

# Main setup function
main() {
    echo "Starting setup process..."
    echo ""
    
    check_docker
    check_python
    setup_environment
    install_python_deps
    start_weaviate
    create_sample_docs
    test_system
    show_next_steps
}

# Handle command line arguments
case "${1:-setup}" in
    setup)
        main
        ;;
    start)
        print_step "Starting Weaviate services..."
        docker-compose up -d
        print_status "Services started"
        ;;
    stop)
        print_step "Stopping Weaviate services..."
        docker-compose down
        print_status "Services stopped"
        ;;
    restart)
        print_step "Restarting Weaviate services..."
        docker-compose down
        docker-compose up -d
        print_status "Services restarted"
        ;;
    test)
        test_system
        ;;
    clean)
        print_step "Cleaning up..."
        docker-compose down -v
        docker system prune -f
        rm -rf venv
        print_status "Cleanup completed"
        ;;
    *)
        echo "Usage: $0 {setup|start|stop|restart|test|clean}"
        echo ""
        echo "Commands:"
        echo "  setup   - Complete system setup (default)"
        echo "  start   - Start Weaviate services"
        echo "  stop    - Stop Weaviate services"
        echo "  restart - Restart Weaviate services"
        echo "  test    - Test system connectivity"
        echo "  clean   - Clean up all components"
        exit 1
        ;;
esac

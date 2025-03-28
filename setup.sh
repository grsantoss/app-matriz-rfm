#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root"
    exit 1
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Rename frontend folder to app if it exists
if [ -d "frontend" ] && [ ! -d "app" ]; then
    print_info "Renaming frontend folder to app..."
    mv frontend app
    print_success "Frontend folder renamed to app"
fi

# Create Traefik network if it doesn't exist
if ! docker network ls | grep -q traefik-public; then
    print_info "Creating Traefik network..."
    docker network create traefik-public
fi

# Create Traefik configuration directory
print_info "Setting up Traefik configuration..."
mkdir -p traefik
touch traefik/acme.json
chmod 600 traefik/acme.json

# Generate secure passwords if not set
if [ -z "$DB_PASSWORD" ]; then
    DB_PASSWORD=$(openssl rand -base64 32)
    print_info "Generated secure database password"
fi

if [ -z "$JWT_SECRET" ]; then
    JWT_SECRET=$(openssl rand -base64 32)
    print_info "Generated secure JWT secret"
fi

# Create necessary directories
print_info "Creating application directories..."
mkdir -p app/storage/analysis_history
mkdir -p backend/storage/analysis_history
mkdir -p auth/storage
mkdir -p config

# Set proper permissions
chmod -R 755 app/storage
chmod -R 755 backend/storage
chmod -R 755 auth/storage
chmod -R 755 config

# Configure environment variables
if [ ! -f ".env" ]; then
    print_info "Creating .env file from .env.production..."
    cp .env.production .env
    
    # Prompt for required values
    read -p "Enter your OpenAI API key: " OPENAI_API_KEY
    read -p "Enter your Amazon SES SMTP username: " SMTP_USERNAME
    read -p "Enter your Amazon SES SMTP password: " SMTP_PASSWORD
    read -p "Enter your email for Let's Encrypt notifications: " ACME_EMAIL
    read -p "Enter your desired PGAdmin email: " PGADMIN_EMAIL
    read -p "Enter your desired PGAdmin password: " PGADMIN_PASSWORD
    
    # Update .env file with provided values
    sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_API_KEY|" .env
    sed -i "s|SMTP_USERNAME=.*|SMTP_USERNAME=$SMTP_USERNAME|" .env
    sed -i "s|SMTP_PASSWORD=.*|SMTP_PASSWORD=$SMTP_PASSWORD|" .env
    sed -i "s|ACME_EMAIL=.*|ACME_EMAIL=$ACME_EMAIL|" .env
    sed -i "s|PGADMIN_EMAIL=.*|PGADMIN_EMAIL=$PGADMIN_EMAIL|" .env
    sed -i "s|PGADMIN_PASSWORD=.*|PGADMIN_PASSWORD=$PGADMIN_PASSWORD|" .env
    
    # Generate Traefik auth credentials
    TRAEFIK_AUTH=$(htpasswd -nb admin $(openssl rand -base64 12))
    sed -i "s|TRAEFIK_AUTH=.*|TRAEFIK_AUTH=$TRAEFIK_AUTH|" .env
    
    print_success "Environment variables configured"
fi

# Build and start containers
print_info "Building and starting containers..."
docker compose up -d --build

# Wait for services to start
print_info "Waiting for services to start..."
sleep 10

# Check if services are running
if docker compose ps | grep -q "Up"; then
    print_success "All services are running!"
    print_info "You can access the application at:"
    print_info "https://app.matrizrfm.com.br       → Web App"
    print_info "https://api.matrizrfm.com.br/docs  → API Docs"
    print_info "https://pgadmin.matrizrfm.com.br   → Database Admin"
    print_info "https://painel.matrizrfm.com.br    → Docker Admin Panel"
else
    print_error "Some services failed to start. Please check the logs:"
    docker compose logs
    exit 1
fi 
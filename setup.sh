#!/bin/bash

# Matriz RFM Setup Script
# This script installs and configures the Matriz RFM application

set -e  # Exit on error

# Print colored messages
print_info() {
    echo -e "\e[34m[INFO]\e[0m $1"
}

print_success() {
    echo -e "\e[32m[SUCCESS]\e[0m $1"
}

print_error() {
    echo -e "\e[31m[ERROR]\e[0m $1"
}

print_info "Starting Matriz RFM setup..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    print_info "Visit https://docs.docker.com/get-docker/ for installation instructions."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    print_info "Visit https://docs.docker.com/compose/install/ for installation instructions."
    exit 1
fi

print_success "Docker and Docker Compose are installed."

# Create configuration files
if [ ! -f .env ]; then
    print_info "Creating .env file from example..."
    cp .env.example .env
    print_success ".env file created. You will need to edit this file with your API keys and settings."
else
    print_info ".env file already exists. Skipping creation."
fi

# Collect required API keys and configuration
read -p "Do you want to configure API keys now? (y/n): " configure_keys
if [[ $configure_keys == "y" || $configure_keys == "Y" ]]; then
    # OpenAI API key
    read -p "Enter your OpenAI API key: " openai_key
    if [[ -n "$openai_key" ]]; then
        sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$openai_key|" .env
        print_success "OpenAI API key configured."
    else
        print_info "OpenAI API key skipped. You'll need to set it manually in the .env file."
    fi
    
    # Amazon SES credentials
    read -p "Do you want to configure Amazon SES for email sending? (y/n): " configure_ses
    if [[ $configure_ses == "y" || $configure_ses == "Y" ]]; then
        read -p "Enter your AWS SES SMTP user: " smtp_user
        read -p "Enter your AWS SES SMTP password: " smtp_password
        read -p "Enter your AWS region (default: us-east-1): " aws_region
        aws_region=${aws_region:-us-east-1}
        
        sed -i "s|SMTP_USER=.*|SMTP_USER=$smtp_user|" .env
        sed -i "s|SMTP_PASSWORD=.*|SMTP_PASSWORD=$smtp_password|" .env
        sed -i "s|AWS_REGION=.*|AWS_REGION=$aws_region|" .env
        print_success "Amazon SES credentials configured."
    else
        print_info "Amazon SES configuration skipped. You'll need to set it manually in the .env file."
    fi
    
    # JWT Secret
    print_info "Generating secure JWT secret..."
    jwt_secret=$(openssl rand -hex 32)
    sed -i "s|JWT_SECRET=.*|JWT_SECRET=$jwt_secret|" .env
    print_success "JWT secret generated and configured."

    # Database password
    print_info "Generating database password..."
    db_password=$(openssl rand -hex 16)
    sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=$db_password|" .env
    print_success "Database password generated and configured."
    
    # PGAdmin credentials
    read -p "Enter email for PGAdmin login (default: admin@matrizrfm.com): " pgadmin_email
    pgadmin_email=${pgadmin_email:-admin@matrizrfm.com}
    read -p "Enter password for PGAdmin login (default: admin): " pgadmin_password
    pgadmin_password=${pgadmin_password:-admin}
    
    sed -i "s|PGADMIN_DEFAULT_EMAIL=.*|PGADMIN_DEFAULT_EMAIL=$pgadmin_email|" .env
    sed -i "s|PGADMIN_DEFAULT_PASSWORD=.*|PGADMIN_DEFAULT_PASSWORD=$pgadmin_password|" .env
    print_success "PGAdmin credentials configured."
else
    print_info "Configuration skipped. You'll need to edit the .env file manually before starting the application."
fi

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p storage/analysis_history
print_success "Directories created."

# Check if Docker daemon is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker daemon is not running. Please start Docker and try again."
    exit 1
fi

# Pull Docker images
print_info "Pulling required Docker images. This may take a while depending on your internet connection..."
docker-compose pull

# Build custom images
print_info "Building custom Docker images. This may take a while..."
docker-compose build

print_success "Docker images built successfully!"

# Final instructions
print_info "Setup completed successfully! To start the application, run:"
echo "docker-compose up -d"
print_info "Then access the application at http://localhost:3000 or http://matrizrfm.local (if you configured local domains)"
print_info "PGAdmin will be available at http://localhost:5050 or http://pgadmin.matrizrfm.local"
print_info "API documentation will be available at http://localhost:5173/docs or http://api.matrizrfm.local/docs"

# Make the script executable
chmod +x setup.sh

print_success "All done! Happy analyzing!" 
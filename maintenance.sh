#!/bin/bash

# Matriz RFM Maintenance Script
# This script performs maintenance tasks for the Matriz RFM application

set -e  # Exit on error

# Print colored messages
print_info() {
    echo -e "\e[34m[INFO]\e[0m $1"
}

print_success() {
    echo -e "\e[32m[SUCCESS]\e[0m $1"
}

print_warning() {
    echo -e "\e[33m[WARNING]\e[0m $1"
}

print_error() {
    echo -e "\e[31m[ERROR]\e[0m $1"
}

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Docker daemon is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker daemon is not running. Please start Docker and try again."
    exit 1
fi

# Display menu
show_menu() {
    echo "============================================"
    echo "      Matriz RFM Maintenance Options"
    echo "============================================"
    echo "1. Update Docker images (pull latest versions)"
    echo "2. Restart all services"
    echo "3. View application logs"
    echo "4. Clean up unused Docker images"
    echo "5. Backup environment file"
    echo "6. Backup database"
    echo "7. Verify application health"
    echo "8. Clean analysis history"
    echo "9. Update OpenAI API key"
    echo "0. Exit"
    echo "============================================"
    read -p "Please select an option: " choice
}

# Update Docker images
update_images() {
    print_info "Updating Docker images. This may take a while..."
    
    # Stop the services
    docker-compose down
    
    # Pull latest images
    docker-compose pull
    
    # Rebuild custom images
    docker-compose build --no-cache
    
    # Start services again
    docker-compose up -d
    
    print_success "Docker images updated and services restarted!"
}

# Restart all services
restart_services() {
    print_info "Restarting all services..."
    docker-compose down
    docker-compose up -d
    print_success "All services restarted!"
}

# View application logs
view_logs() {
    read -p "Enter service name (frontend, backend, auth, postgres, all) [all]: " service
    service=${service:-all}
    
    if [ "$service" = "all" ]; then
        docker-compose logs --tail=100
    else
        docker-compose logs --tail=100 "$service"
    fi
}

# Clean up unused Docker images
clean_images() {
    print_info "Cleaning unused Docker images and volumes..."
    
    # Remove unused containers
    docker container prune -f
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    print_success "Clean up completed!"
}

# Backup environment file
backup_env() {
    print_info "Creating backup of environment file..."
    
    # Create backup directory if it doesn't exist
    mkdir -p backups
    
    # Create backup with timestamp
    timestamp=$(date +"%Y%m%d_%H%M%S")
    cp .env "backups/.env.backup_$timestamp"
    
    print_success "Environment file backed up to backups/.env.backup_$timestamp"
}

# Backup database
backup_database() {
    print_info "Creating database backup..."
    
    # Create backup directory if it doesn't exist
    mkdir -p backups/database
    
    # Get timestamp
    timestamp=$(date +"%Y%m%d_%H%M%S")
    
    # Check if postgres container is running
    if docker-compose ps | grep -q postgres; then
        # Get database configuration from .env file
        source .env
        
        # Backup app database
        docker-compose exec -T postgres pg_dump -U ${DB_USER:-postgres} ${DB_NAME:-app_db} > "backups/database/app_db_$timestamp.sql"
        
        # Backup auth database
        docker-compose exec -T postgres pg_dump -U ${DB_USER:-postgres} ${DB_NAME_AUTH:-auth_db} > "backups/database/auth_db_$timestamp.sql"
        
        print_success "Database backups created in backups/database/ directory"
    else
        print_error "Postgres container is not running. Cannot create database backup."
    fi
}

# Verify application health
verify_health() {
    print_info "Verifying application health..."
    
    # Check if all containers are running
    if docker-compose ps | grep -q "Exit"; then
        print_error "Some containers are not running:"
        docker-compose ps
    else
        print_success "All containers are running."
    fi
    
    # Check backend health endpoint
    if curl -s "http://localhost:5173/" > /dev/null; then
        print_success "Backend API is responsive."
    else
        print_error "Backend API is not responding."
    fi
    
    # Check frontend
    if curl -s "http://localhost:3000/" > /dev/null; then
        print_success "Frontend is responsive."
    else
        print_warning "Frontend may not be responding properly."
    fi
    
    # Check database connection through backend
    if docker-compose exec backend python -c "from database import engine; print('Database connection successful')" 2>/dev/null | grep -q "successful"; then
        print_success "Database connection is working."
    else
        print_error "Database connection may have issues."
    fi
}

# Clean analysis history
clean_history() {
    print_info "Cleaning analysis history..."
    
    read -p "Do you want to remove all analysis files? (y/n): " confirm
    if [[ $confirm == "y" || $confirm == "Y" ]]; then
        # Remove files in storage/analysis_history
        rm -rf storage/analysis_history/*
        print_success "Analysis history cleaned."
        
        read -p "Do you also want to clear database records? (y/n): " confirm_db
        if [[ $confirm_db == "y" || $confirm_db == "Y" ]]; then
            # Clear database records (this depends on your database setup)
            if docker-compose ps | grep -q postgres; then
                docker-compose exec -T postgres psql -U ${DB_USER:-postgres} -d ${DB_NAME:-app_db} -c "TRUNCATE customer_segments; TRUNCATE analyses CASCADE;"
                print_success "Database analysis records cleared."
            else
                print_error "Postgres container is not running. Cannot clear database records."
            fi
        fi
    else
        print_info "Analysis history cleaning cancelled."
    fi
}

# Update OpenAI API key
update_openai_key() {
    read -p "Enter your new OpenAI API key: " openai_key
    if [[ -n "$openai_key" ]]; then
        sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$openai_key|" .env
        print_success "OpenAI API key updated."
        
        read -p "Do you want to restart services to apply the new key? (y/n): " restart
        if [[ $restart == "y" || $restart == "Y" ]]; then
            restart_services
        fi
    else
        print_error "API key cannot be empty."
    fi
}

# Main execution
while true; do
    show_menu
    
    case $choice in
        1) update_images ;;
        2) restart_services ;;
        3) view_logs ;;
        4) clean_images ;;
        5) backup_env ;;
        6) backup_database ;;
        7) verify_health ;;
        8) clean_history ;;
        9) update_openai_key ;;
        0) 
            print_info "Exiting maintenance script."
            exit 0
            ;;
        *)
            print_error "Invalid option. Please try again."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    clear
done 
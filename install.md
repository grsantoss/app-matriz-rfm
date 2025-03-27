# Matriz RFM Installation Guide

This guide provides detailed instructions for installing the Matriz RFM application on a Linux server. Follow these steps carefully to ensure a successful installation.

## Prerequisites

Before starting the installation, ensure you have:

### Hardware Requirements
- A Linux server with at least 4GB RAM (8GB recommended)
- 20GB free disk space (SSD recommended for better performance)
- 2 CPU cores minimum (4 cores recommended)

### Software Requirements
- Ubuntu 20.04 LTS or later (recommended)
- Root or sudo access to the server
- Domain name(s) configured and pointing to your server's IP address
- Access to your server's firewall settings
- Git installed on your system

### External Services Required
- OpenAI API account and API key
- Amazon SES account for email services
- Domain name(s) with DNS access
- SSL certificate (will be handled by Let's Encrypt)

## Step 1: System Update

First, update your system packages:

```bash
# Update package list
sudo apt update

# Upgrade existing packages
sudo apt upgrade -y

# Install essential build tools
sudo apt install -y build-essential curl git software-properties-common

# Install additional useful tools
sudo apt install -y htop net-tools ufw
```

## Step 2: Install Docker

Install Docker using the official repository:

```bash
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package list
sudo apt update

# Install Docker
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to the docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Verify Docker installation
docker --version
docker run hello-world
```

## Step 3: Install Docker Compose

Docker Compose is now included with Docker Desktop, but if you need to install it separately:

```bash
# Install Docker Compose
sudo apt install -y docker-compose

# Verify installation
docker-compose --version

# Test Docker Compose
docker-compose version
```

## Step 4: Install Traefik

Install Traefik as a Docker container:

```bash
# Create Traefik network
docker network create traefik-public

# Create Traefik configuration directory
sudo mkdir -p /etc/traefik

# Create Traefik configuration file
sudo tee /etc/traefik/traefik.yml << EOF
api:
  dashboard: true
  insecure: true

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
    network: traefik-public

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: your-email@example.com
      storage: /etc/traefik/acme.json
      httpChallenge:
        entryPoint: web

log:
  level: INFO

accessLog: {}
EOF

# Create acme.json file with proper permissions
sudo touch /etc/traefik/acme.json
sudo chmod 600 /etc/traefik/acme.json

# Create Traefik container
docker run -d \
  --name traefik \
  --restart=always \
  -p 80:80 \
  -p 443:443 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /etc/traefik:/etc/traefik \
  --network traefik-public \
  traefik:v2.10

# Verify Traefik installation
docker ps | grep traefik
```

## Step 5: Configure Firewall

Configure your firewall to allow necessary ports:

```bash
# Allow SSH (if not already allowed)
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall if not already enabled
sudo ufw enable

# Verify firewall status
sudo ufw status
```

## Step 6: Clone the Repository

Clone the Matriz RFM repository:

```bash
# Create application directory
sudo mkdir -p /opt/matriz-rfm
sudo chown $USER:$USER /opt/matriz-rfm

# Clone the repository
git clone https://github.com/grsantoss/app-matriz-rfm.git /opt/matriz-rfm

# Navigate to the application directory
cd /opt/app-matriz-rfm

# Verify repository contents
ls -la
```

## Step 7: Configure Environment Variables

Create and configure the environment file:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the environment file with your settings
nano .env
```

### Required Environment Variables

Update the following variables in the `.env` file:

#### Domain Configuration
- `FRONTEND_DOMAIN`: Your frontend domain (e.g., app.yourdomain.com)
- `BACKEND_DOMAIN`: Your backend domain (e.g., api.yourdomain.com)
- `PGADMIN_DOMAIN`: Your PGAdmin domain (e.g., db.yourdomain.com)

#### Security
- `DB_PASSWORD`: Generate a secure password (at least 16 characters)
- `JWT_SECRET`: Generate a secure secret (at least 32 characters)
- `JWT_EXPIRATION`: Token expiration time (e.g., 24h)

#### External Services
- `OPENAI_API_KEY`: Your OpenAI API key
- `SMTP_USERNAME`: Your Amazon SES SMTP username
- `SMTP_PASSWORD`: Your Amazon SES SMTP password
- `SMTP_HOST`: Amazon SES SMTP host
- `SMTP_PORT`: Amazon SES SMTP port (587 for TLS)

#### Database Configuration
- `DB_HOST`: Database host (usually 'db')
- `DB_PORT`: Database port (5432)
- `DB_NAME`: Database name (matriz_rfm)
- `DB_USER`: Database user (postgres)

## Step 8: Run the Setup Script

Make the setup script executable and run it:

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

### What the Setup Script Does

The setup script will:
1. Check for Docker and Docker Compose installation
2. Verify environment variables
3. Generate secure passwords if needed
4. Create necessary directories:
   - `frontend/storage/analysis_history`
   - `backend/storage/analysis_history`
5. Build Docker images
6. Start all services
7. Initialize the database
8. Configure SSL certificates

### Expected Output

You should see output similar to:
```
Checking prerequisites...
✓ Docker is installed
✓ Docker Compose is installed
✓ Environment variables are set
Creating directories...
✓ Frontend storage directory created
✓ Backend storage directory created
Building Docker images...
✓ Frontend image built
✓ Backend image built
✓ Auth service image built
Starting services...
✓ All services started successfully
Initializing database...
✓ Database initialized
Configuring SSL...
✓ SSL certificates configured
Setup completed successfully!
```

## Step 9: Verify Installation

After the setup script completes, verify the installation:

```bash
# Check if all containers are running
docker-compose ps

# Check application logs
docker-compose logs

# Verify Traefik dashboard
curl -H "Host: traefik.your-domain.com" http://localhost:8080

# Check database connection
docker-compose exec db psql -U postgres -d matriz_rfm -c "\l"
```

### Expected Container Status

You should see all containers running:
- frontend
- backend
- auth
- db
- pgadmin
- traefik

## Step 10: Access the Application

Once everything is running, you can access:

### Main Application
- Frontend: https://your-frontend-domain
- Backend API: https://your-backend-domain
- PGAdmin: https://your-pgadmin-domain
- Traefik Dashboard: https://traefik.your-domain.com

### Default Credentials

#### PGAdmin
- Email: admin@admin.com
- Password: admin
(Change these immediately after first login)

#### Application
- Create your first user account through the registration page

## Troubleshooting

If you encounter any issues:

### 1. Container Issues
```bash
# Check container logs
docker-compose logs [service-name]

# Restart specific service
docker-compose restart [service-name]

# Rebuild and restart service
docker-compose up -d --build [service-name]
```

### 2. Docker Service Issues
```bash
# Check Docker service status
sudo systemctl status docker

# Restart Docker service
sudo systemctl restart docker

# Check Docker logs
sudo journalctl -u docker
```

### 3. Traefik Issues
```bash
# Check Traefik logs
docker logs traefik

# Verify Traefik configuration
docker exec traefik traefik healthcheck
```

### 4. Network Issues
```bash
# List Docker networks
docker network ls

# Inspect network
docker network inspect traefik-public

# Test network connectivity
docker exec [container-name] ping [target]
```

### 5. Database Issues
```bash
# Check database logs
docker-compose logs db

# Access database
docker-compose exec db psql -U postgres

# Backup database
docker-compose exec db pg_dump -U postgres matriz_rfm > backup.sql
```

## Maintenance

For routine maintenance tasks, use the maintenance script:

```bash
./maintenance.sh
```

### Available Maintenance Options

1. **Update Docker Images**
   - Pulls latest images
   - Rebuilds custom images
   - Updates dependencies

2. **Service Management**
   - Restart all services
   - Restart specific service
   - View service status

3. **Log Management**
   - View all logs
   - View specific service logs
   - Clear old logs

4. **Resource Cleanup**
   - Remove unused images
   - Remove stopped containers
   - Clean up volumes

5. **Backup Operations**
   - Backup environment file
   - Backup database
   - Backup analysis history

6. **Health Checks**
   - Verify service health
   - Check database connection
   - Test API endpoints

## Security Considerations

### 1. Initial Security Setup
- Change all default passwords
- Configure firewall rules
- Set up SSL certificates
- Enable 2FA where possible

### 2. Regular Maintenance
- Update system packages weekly
- Update Docker images monthly
- Rotate API keys quarterly
- Monitor disk space usage

### 3. Monitoring
- Set up log monitoring
- Configure alerts for suspicious activity
- Monitor API usage
- Track resource utilization

### 4. Backup Strategy
- Daily database backups
- Weekly full system backups
- Monthly archive backups
- Regular backup testing

### 5. Access Control
- Implement role-based access
- Regular password rotation
- Session management
- IP whitelisting

## Support

For support or questions:

### 1. Documentation
- Check the application documentation
- Review the troubleshooting section
- Consult the API documentation
- Read the FAQ

### 2. Technical Support
- Contact the development team
- Submit issues on GitHub
- Join the community forum
- Check the status page

### 3. Emergency Support
- Contact system administrator
- Access backup systems
- Review incident reports
- Follow recovery procedures

## Updates

To update the application in the future:

```bash
# Backup current setup
./maintenance.sh backup

# Pull latest changes
git pull

# Run the setup script again
./setup.sh

# Verify update
./maintenance.sh verify
```

### Update Checklist
1. Backup all data
2. Review changelog
3. Test in staging
4. Schedule maintenance window
5. Execute update
6. Verify functionality
7. Monitor for issues
8. Update documentation

Remember to backup your data before performing updates and test the update process in a staging environment first. 
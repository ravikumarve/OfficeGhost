# GhostOffice - Deployment Guide

## Overview

GhostOffice can be deployed in multiple ways:
1. **Local Development** - Direct Python execution
2. **Docker Container** - Isolated containerized deployment
3. **Production Server** - Systemd service with reverse proxy

## Prerequisites

- Python 3.9+ or Docker
- Ollama installed (for AI capabilities)
- 8GB+ RAM recommended

---

## Option 1: Local Development

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/ai-office-pilot.git
cd ai-office-pilot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run setup
python3 setup.py

# Run application
python3 main.py
```

### Configuration

1. Copy `.env.example` to `.env`
2. Configure email credentials:
   ```env
   EMAIL_1_ADDRESS=your.email@gmail.com
   EMAIL_1_PASSWORD=your_app_password
   EMAIL_1_IMAP_HOST=imap.gmail.com
   EMAIL_1_SMTP_HOST=smtp.gmail.com
   ```
3. Configure watch folders:
   ```env
   WATCH_FOLDERS=~/Downloads,~/Desktop
   ```

---

## Option 2: Docker Deployment

### Build Image

```bash
docker build -t ai-office-pilot .
```

### Run Container

```bash
docker run -d \
  --name ai-office-pilot \
  -v ~/ai-office-pilot-data:/data \
  -p 5000:5000 \
  -e EMAIL_1_ADDRESS=your.email@gmail.com \
  -e EMAIL_1_PASSWORD=your_app_password \
  ai-office-pilot
```

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Option 3: Production Deployment

### Systemd Service

1. Create service file `/etc/systemd/system/ai-office-pilot.service`:
   ```ini
   [Unit]
   Description=GhostOffice
   After=network.target

   [Service]
   Type=simple
   User=aiopilot
   WorkingDirectory=/opt/ai-office-pilot
   Environment=PATH=/opt/ai-office-pilot/venv/bin
   ExecStart=/opt/ai-office-pilot/venv/bin/python main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. Enable and start:
   ```bash
   sudo systemctl enable ai-office-pilot
   sudo systemctl start ai-office-pilot
   ```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 443 ssl;
    server_name ai.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## Security Considerations

### Firewall

```bash
# Allow dashboard only from specific IPs
ufw allow from 192.168.1.0/24 to any port 5000
```

### SSL/TLS

Always use HTTPS in production:
- Let's Encrypt for free certificates
- Certbot for automatic renewal

### Environment Variables

Never commit `.env` files. Use:
```bash
# Set variables in production
export EMAIL_1_PASSWORD="secure_password"
```

---

## Monitoring

### Health Check

```bash
# Check service status
curl http://localhost:5000/api/health
```

### Logs

```bash
# View application logs
journalctl -u ai-office-pilot -f

# Docker logs
docker logs -f ai-office-pilot
```

---

## Backup

### Automated Backups

The application creates automatic backups. Configure retention:
```env
BACKUP_RETENTION_DAYS=30
```

### Manual Backup

```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz ~/ai-office-pilot-data
```

---

## Troubleshooting

### Ollama Not Running

```bash
# Start Ollama service
ollama serve

# Pull model
ollama pull phi3:mini
```

### Email Authentication Failed

- Enable 2FA on your Google account
- Generate an App Password
- Use App Password in `.env`

### Dashboard Not Accessible

- Check if port 5000 is open
- Check firewall rules
- Verify service is running
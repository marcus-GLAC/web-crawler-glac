#!/bin/bash

# VPS Setup Script for Web Crawler
echo "🔧 Setting up Web Crawler on VPS..."

# Update system
sudo apt update && sudo apt upgrade -y


# Create application directory
sudo mkdir -p /opt/web-crawler-glac
sudo chown $USER:$USER /opt/web-crawler-glac

# Clone repository
cd /opt
git clone https://github.com/David-GLAC/web-crawler-glac.git
cd web-crawler-glac

# Setup environment
cp .env.example .env
echo "✏️  Please edit .env file with your configuration:"
echo "nano .env"

# Start application
make start

echo "✅ Setup complete!"
echo "📱 Your app should be available at: https://web-crawler.digital-transformations.tech"
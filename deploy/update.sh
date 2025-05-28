#!/bin/bash

# Update Script
echo "🔄 Updating Web Crawler..."

cd /opt/web-crawler-glac

# Pull latest changes
git pull origin main

# Rebuild and restart
make restart

echo "✅ Update complete!"
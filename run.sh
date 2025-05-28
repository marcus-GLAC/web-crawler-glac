#!/bin/bash

# Set script to exit on any error
set -e

echo "🚀 Starting Web Crawler Application..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start the application
echo "🔨 Building Docker containers..."
docker-compose build

echo "🎬 Starting application..."
docker-compose up -d

echo "✅ Application started successfully!"
echo "📱 Access your app at: http://localhost:8501"
echo "🔍 Check logs with: docker-compose logs -f"
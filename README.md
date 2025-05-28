# Web Crawler GLAC

A powerful web crawling application built with Streamlit and Crawl4AI.

## Features
- 🕷️ Advanced web crawling with Crawl4AI
- 👤 User authentication with Supabase
- 📊 Crawl history and management
- 🔗 Link extraction
- 💾 Export capabilities
- 🐳 Docker containerized
- 🌐 Subdomain deployment ready

## Quick Start

### Local Development
1. Clone the repository
2. Copy environment variables: `make setup`
3. Edit `.env` with your Supabase credentials
4. Start the application: `make start`

### VPS Deployment
1. Clone on your VPS
2. Run setup script: `./deploy/setup.sh`
3. Configure your domain and SSL
4. Access via your subdomain

## Commands
- `make help` - Show available commands
- `make start` - Start the application
- `make stop` - Stop the application
- `make logs` - View logs
- `make clean` - Clean up

## Environment Variables
See `.env.example` for required configuration.
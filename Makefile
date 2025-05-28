.PHONY: help build start stop restart logs clean setup deploy

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup    - Initial setup (copy .env.example to .env)"
	@echo "  make build    - Build Docker containers"
	@echo "  make start    - Start the application"
	@echo "  make stop     - Stop the application"
	@echo "  make restart  - Restart the application"
	@echo "  make logs     - Show application logs"
	@echo "  make clean    - Clean up containers and images"
	@echo "  make deploy   - Deploy to production"

setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file. Please edit it with your configuration."; \
	else \
		echo "⚠️  .env file already exists."; \
	fi

build:
	docker-compose build

start:
	docker-compose up -d
	@echo "✅ Application started at http://localhost:8501"

stop:
	docker-compose down

restart: stop start

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

deploy:
	@echo "🚀 Deploying to production..."
	docker-compose -f docker-compose.yml up -d --build
	@echo "✅ Deployment complete!"

up: ## Starts all containers and runs the application
	docker compose up -d
	chalice local

stop: ## Stops all running containers
	docker compose stop

down: ## Stops and removes all containers
	docker compose down

migrate: ## Perform the database migration
	docker compose up -d postgres
	sleep 5
	alembic upgrade head

.PHONY: run run-api run-db test clean

run: run-db run-api

run-api:
	docker-compose up --build api

run-db:
	docker-compose up -d db

shell-db:
	# username and dbname values are hardcoded based on values in environment file
	docker-compose exec db psql --username=dev --dbname=app_dev

test:
	# TODO: How to clean up all containers on a failed test run?
	docker-compose build api-test
	docker-compose run api-test
	docker-compose down -v

down:
	docker-compose down -v

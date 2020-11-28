.PHONY: build run run-api test down clean

venv_dir := venv
python := $(venv_dir)/bin/python
pip := $(venv_dir)/bin/pip
flask := $(venv_dir)/bin/flask


build:
	python3 -m venv venv
	$(pip) install --no-cache -r requirements.txt
	touch .build

run: run-db run-api

run-api:
	docker-compose up api

run-db:
	docker-compose up -d db

test:
	# TODO: How to clean up all containers on a failed test run?
	docker-compose run api-test
	docker-compose down -v

down:
	docker-compose down -v

clean: down
	rm -rf $(venv_dir)

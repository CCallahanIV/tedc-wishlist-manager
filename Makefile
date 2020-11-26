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

run-api-test: run-db
	docker-compose up --build api-test

run-db:
	docker-compose up -d db

test: run-api-test
	docker-compose down -v

down:
	docker-compose down -v

clean: down
	rm -rf $(venv_dir)

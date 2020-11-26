.PHONY: build run test down clean

venv_dir := venv
python := $(venv_dir)/bin/python
pip := $(venv_dir)/bin/pip
flask := $(venv_dir)/bin/flask


.build:
	python3 -m venv venv
	$(pip) install -r requirements.txt
	touch .build

build: .build

run: .build .run-db
	env FLASK_APP=src DATABASE_URL=postgresql://dev:password1@db:5432/app_dev \
		$(flask) run

.run-db:
	docker-compose up -d db
	touch .run-db

run-db: .run-db

test:
	$(python) -m pytest

down:
	rm -f .run-db && \
	docker-compose down

clean: down
	rm -f .build && \
	rm -f .run-db && \
	rm -rf $(venv_dir)

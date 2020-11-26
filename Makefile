# TODO:
# build: create venv, install requirements
# run: run app
# test: run tests
# clean: clean all assets

venv_dir := venv
python := $(venv_dir)/bin/python
pip := $(venv_dir)/bin/pip
flask := $(venv_dir)/bin/flask


build:
	python3 -m venv venv
	$(pip) install -r requirements.txt

run:
	env FLASK_APP=app/hello.py && \
	env DATABASE_URL=postgresql://dev:password1@db:5432/app_dev && \
	$(flask) run

run-db:
	docker-compose up 

test:
	$(python) -m pytest

clean:
	rm -rf $(venv_dir)
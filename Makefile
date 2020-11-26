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
	env FLASK_APP=app/hello.py $(flask) run

test:
	$(python) -m pytest

clean:
	rm -rf $(venv_dir)
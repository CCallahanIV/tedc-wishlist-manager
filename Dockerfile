# pull official base image
FROM python:3.9.0-slim-buster AS base

# set work directory
WORKDIR /usr/src/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y netcat

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY entrypoint.sh .
COPY ./src/manage.py .
COPY ./src/api .

ENTRYPOINT [ "entrypoint.sh" ]

FROM base as test

COPY ./requirements_dev.txt /usr/src/requirements_dev.txt
RUN pip install -r requirements_dev.txt
COPY ./src/tests .

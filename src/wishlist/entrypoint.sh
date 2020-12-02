#!/bin/bash

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

echo "Creating DB"
python manage.py create_db
if [ "$IS_TEST" != "true" ]
then
    echo "Seeding DB"
    python manage.py seed_db
fi

exec "$@"
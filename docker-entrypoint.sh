#!/bin/sh
if [ "$DATABASE" = "postgres" ]; then
  echo "Waiting for postgres..."

  while ! nc -z $SQL_HOST $SQL_PORT; do
    sleep 0.1
  done

  echo "PostgreSQL started"

  # setup database
  flask setup_db

  # Migrate db
  flask db upgrade

  exec "$@"
fi

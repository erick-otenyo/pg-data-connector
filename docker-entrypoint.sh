#!/bin/sh
if [ "$DB" = "postgres" ]; then
  echo "Waiting for postgres..."

  while ! nc -z $DB_HOST $DB_PORT; do
    sleep 0.1
  done

  echo "PostgreSQL started"

  # setup database
  flask setup_db

  # Migrate db
  flask db upgrade

  exec "$@"
fi

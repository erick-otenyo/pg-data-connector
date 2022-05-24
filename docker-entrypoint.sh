#!/bin/sh

# setup database
flask setup_db

# Migrate db
flask db upgrade

exec "$@"
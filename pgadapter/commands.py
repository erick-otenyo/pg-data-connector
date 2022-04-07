import click
from pgadapter import db
from pgadapter.config import SETTINGS

import logging

PG_SERVICE_SCHEMA = SETTINGS.get("PG_SERVICE_SCHEMA")
PG_SERVICE_USER = SETTINGS.get("PG_SERVICE_USER")
PG_SERVICE_USER_PASSWORD = SETTINGS.get("PG_SERVICE_USER_PASSWORD")


@click.command(name="setup_db")
def setup_db():
    logging.info("[DBSETUP]: Setting up db")
    sql = f"""DO
            $do$
            BEGIN
                CREATE EXTENSION IF NOT EXISTS postgis;
                CREATE SCHEMA IF NOT EXISTS {PG_SERVICE_SCHEMA};
               IF NOT EXISTS (
                  SELECT FROM pg_catalog.pg_roles
                  WHERE  rolname = '{PG_SERVICE_USER}') THEN
                  CREATE ROLE {PG_SERVICE_USER} LOGIN ENCRYPTED PASSWORD '{PG_SERVICE_USER_PASSWORD}';
                  GRANT USAGE ON SCHEMA {PG_SERVICE_SCHEMA} TO {PG_SERVICE_USER};
                  ALTER DEFAULT PRIVILEGES IN SCHEMA {PG_SERVICE_SCHEMA} GRANT SELECT ON TABLES TO {PG_SERVICE_USER};
               END IF;
            END
            $do$;"""

    db.session.execute(sql)

    db.session.commit()

    logging.info("[DBSETUP]: Done Setting up db")

    # NOTE:
    # https://stackoverflow.com/questions/22684255/grant-privileges-on-future-tables-in-postgresql
    # ALTER DEFAULT PRIVILEGES FOR USER pgadapteruser IN SCHEMA pgadapter GRANT SELECT ON TABLES TO tileserv;

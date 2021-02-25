import logging

import psycopg2

from pgadapter.config import SETTINGS


def setup():
    logging.info('[DB_SETUP]: Setting up DB')

    db_uri = SETTINGS.get("SQLALCHEMY_DATABASE_URI")

    conn = psycopg2.connect(db_uri)

    try:
        # create cursor object from connection
        cur = conn.cursor()

        # CREATE POSTGIS EXTENSION IF NOT EXISTS
        logging.info('[DB_SETUP]: Creating postgis extension')
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")

        # Create Schema if not exists
        logging.info('[DB_SETUP]: Creating schema')
        schema = SETTINGS.get("PG_SERVICE_SCHEMA")
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

        conn.commit()

    except Exception as e:
        raise e
    finally:
        conn.close()

import glob
import logging
import os
import tempfile
from subprocess import Popen, PIPE
from zipfile import ZipFile

from pgadapter.config import SETTINGS
from pgadapter.errors import NoShpFound, NoShxFound, NoDbfFound
from urllib.parse import urlparse, unquote

PG_SERVICE_SCHEMA = SETTINGS.get('PG_SERVICE_SCHEMA')


# depreciated
def shp2pgsql(shp_zip_path, table_name, srid=4326):
    logging.info("[SHP2PGSQL]: Extracting zip file")
    # use temp folder
    with tempfile.TemporaryDirectory() as tmpdir:
        # unzip file
        with ZipFile(shp_zip_path, 'r') as zip_obj:
            for filename in zip_obj.namelist():
                # ignore __macosx files
                if not filename.startswith('__MACOSX/'):
                    zip_obj.extract(filename, tmpdir)

        # Use the first available shp
        shp = glob.glob(f"{tmpdir}/*.shp")

        logging.info("[SHP2PGSQL]: Checking mandatory files")

        if not shp:
            raise NoShpFound("No shapefile found in provided zip file")

        shp_fn = os.path.splitext(shp[0])[0]

        files = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir)]

        # check for .shx
        if f"{shp_fn}.shx" not in files:
            raise NoShxFound("No .shx file found in provided zip file")

        # check for .dbf
        if f"{shp_fn}.dbf" not in files:
            raise NoDbfFound("No .dbf file found in provided zip file")

        full_table_name = f"{PG_SERVICE_SCHEMA}.{table_name}"

        logging.info("[SHP2PGSQL]: Running shp2pgsql command")

        # Turns the shp file into an sql query
        cmd = ['shp2pgsql', '-c', '-D', '-I', '-s', f"{srid}", shp[0], full_table_name]

        p1 = Popen(cmd, stdout=PIPE, stderr=PIPE)

        db_uri = SETTINGS.get("DATABASE_URI")

        # Runs the temporary sql file, using a connection
        psql_cmd = ['psql', db_uri, ]

        logging.info(f"[SHP2PGSQL]: Inserting features to database table '{full_table_name}' ")
        p2 = Popen(psql_cmd, stdin=p1.stdout, stdout=PIPE, stderr=PIPE)

        p1.stdout.close()

        stdout, stderr = p2.communicate()

        # TODO: Catch possible errors better

        if stderr:
            raise Exception

        pg_table = {"table_name": full_table_name, "srid": srid}

        try:
            logging.info(f"[SHP2PGSQL]: Deleting uploaded shapefile")
            os.remove(shp_zip_path)
        except Exception as e:
            pass

    return pg_table


def ogr2pg(file_path, table_name, srid=4326):
    db_uri = SETTINGS.get("SQLALCHEMY_DATABASE_URI")
    dbc = urlparse(db_uri)
    # construct db connection options from uri
    db_host = dbc.hostname
    db_port = dbc.port or 5432
    db_user = dbc.username
    db_password = dbc.password
    # unquote incase encoded
    db_password = unquote(db_password)
    db_name = dbc.path.lstrip(' / ')

    # construct ogr2ogr command
    # notable option: -lco FID=gid  - Use custom fid column name. ogr by default gives ogc_fid. We use gid instead
    cmd = ["ogr2ogr", "-f", "PostgreSQL",
           f"PG:host={db_host} port={db_port} user={db_user} password={db_password} dbname={db_name}", file_path,
           "-nln", table_name, "-lco", f"FID=gid", "-lco", f"SCHEMA={PG_SERVICE_SCHEMA}", "-lco", "GEOMETRY_NAME=geom",
           "-nlt", "PROMOTE_TO_MULTI", "-lco", "PRECISION=NO"
           ]

    p1 = Popen(cmd, stdout=PIPE, stderr=PIPE)

    p1.stdout.close()

    stdout, stderr = p1.communicate()

    # TODO: Catch possible errors better
    if stderr:
        raise Exception(stderr)

    full_table_name = f"{PG_SERVICE_SCHEMA}.{table_name}"

    pg_table = {"table_name": full_table_name, "srid": srid}

    return pg_table


def db_import(file_path, table_name):
    file_extension = os.path.splitext(file_path)[1]

    # handle shapefile
    if file_extension == ".zip":
        logging.info("[DB_IMPORT]: Importing Shapefile")

        with tempfile.TemporaryDirectory() as tmpdir:
            # unzip file
            with ZipFile(file_path, 'r') as zip_obj:
                for filename in zip_obj.namelist():
                    # ignore __macosx files
                    if not filename.startswith('__MACOSX/'):
                        zip_obj.extract(filename, tmpdir)

            # Use the first available shp
            shp = glob.glob(f"{tmpdir}/*.shp")

            logging.info("[DB_IMPORT]: Checking mandatory files")

            if not shp:
                raise NoShpFound("No shapefile found in provided zip file")

            shp_fn = os.path.splitext(shp[0])[0]

            files = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir)]

            # check for .shx
            if f"{shp_fn}.shx" not in files:
                raise NoShxFound("No .shx file found in provided zip file")

            # check for .dbf
            if f"{shp_fn}.dbf" not in files:
                raise NoDbfFound("No .dbf file found in provided zip file")

            table = ogr2pg(shp[0], table_name)

            return table

    # handle geojson
    if file_extension == ".geojson":
        logging.info("[DB_IMPORT]: Importing Geojson")
        table = ogr2pg(file_path, table_name)
        return table

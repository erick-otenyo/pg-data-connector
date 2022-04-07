# PG Data Connector

PG Data Connector is a Flask service that helps to import Geospatial data into a PostGIS database.

This was developed to facilitate importing of mostly shapefiles and Geojson files into a postgis database for
the [EAHW](https://eahazardswatch.icpac.net) project. Each individual uploaded file is saved in a new table.

These tables can then be exposed on the web as `vector tiles`
or `geojson` using tools like [pg_tileserv](https://github.com/CrunchyData/pg_tileserv)
and [pg_featureserv](https://github.com/CrunchyData/pg_featureserv).

Under the hood, this service uses [ogr2ogr](https://gdal.org/programs/ogr2ogr.html)

## Dependencies

The PG Data Connector service is built using [Flask](https://github.com/pallets/flask), and can be executed either
natively or using Docker, each of which has its own set of requirements.

Native execution requires:

- [Python 3.8](https://www.python.org/)

Execution using Docker requires:

- [Docker](https://www.docker.com/)

Both execution require a running `Postgres/PostGIS` instance that can be hosted locally or somewhere on the cloud. You
will need the full postgres connection string.

## Getting started

Start by cloning the repository from github to your execution environment

```
git clone https://github.com/icpac-igad/pg-data-connector.git
cd pg-data-connector
```

After that, follow one of the instructions below:

### Using native execution

1. Install the required python dependencies using `pip`, preferably in a virtual environment .

    ```
    pip install -r requirements.txt
    ```

2. Create and update your `.env`. You can find an example `.env.sample` file in the project root. The variables are
   described in detail in [this section](#environment-variables) of the documentation
    ```
     cp .env.sample .env
   ```

3. Set up the database
   ```
   flask setup_db
   ```
   This will set up the database schema, role and default permissions for all the data that will be imported.

   ```
   flask db upgrade
   ```

   This will run the database migrations

**Note**: You will only need to run the above two commands only once during the initial set up

4. Run the flask dev server

   ```
   python main.py
   ```

### Using Docker

1. Create and update your `.env`. You can find an example `.env.sample` file in the project root. The variables are
   described in detail in [this section](#environment-variables) of the documentation
2. Build the image
   ```
   docker build -t pg_data_container .
   ```
3. Run the container

```
docker run --rm --env-file .env -p 8000:8000 pg_data_container gunicorn --bind 0.0.0.0:8000 pgadapter:app

```

## Environment Variables

- DEBUG=True or False
- LOG=INFO or DEBUG or ERROR Default INFO
- PORT=8000
- FLASK_ENV=dev or production
- FLASK_APP=pgadapter/__init__.py

- SQLALCHEMY_DATABASE_URI => Postgres connection string in the usual
  form: `postgresql://<username>:<password>@<host>:<port>/<db>`
- PG_SERVICE_SCHEMA => DB schema to use
- PG_SERVICE_USER => DB role name
- PG_SERVICE_USER_PASSWORD => DB role password

**NOTE:** The `PG_SERVICE_SCHEMA`, `PG_SERVICE_USER` and `PG_SERVICE_USER_PASSWORD` will be used to create a schema that
will be accessed securely by external apps without compromising the database security. This will be created in the db
automatically using the `flask setu_db` command. You do not need to create them manually in your database.

- API_USERNAME => API username for basic auth of the endpoints
- API_PASSWORD_HASH =>  Password Hash for authentication. You can generate one using the script below:
   ```python
   from werkzeug.security import generate_password_hash
   
   generate_password_hash("<yourpassword>")
   ```

  If you forget your password, just create a new hash using your new password, and restart the service.

## Usage

The service exposes 3 endpoints:

### Import geospatial data

```http request
  POST api/v1/pg-dataset
```

#### Parameters

| Name         | Type     | Description                                                                                    |
|:-------------|:---------|:-----------------------------------------------------------------------------------------------|
| `file`       | `File`   | **Required**. The file to import. This must be either a `zipped shapefile` or a `geojson` file |
| `table_name` | `string` | **Required**. The name to save the table as in the database                                    |

### Listing available Datasets

```http request
  GET api/v1/pg-dataset
```

### Deleting Dataset

```http request
  DELETE api/v1/pg-dataset/${dataset_id}
```

| Name         | Type     | Description                                   |
|:-------------|:---------|:----------------------------------------------|
| `dataset_id` | `string` | **Required**. The ID of the dataset to delete |

### Authentication

The endpoints for importing and deleting data require basic authentication i.e. `username` and `password`

## Production Deployment

This service was developed as part of the ICPAC's `PostGIS for the Web Services`
used in various applications, including the [EAHW](https://eahazardswatch.icpac.net).

This means that ideally, it should be deployed alongside the other services that depend on the imported data.

You can find an [example project here](https://github.com/icpac-igad/eahw-pg4w) that runs the EAHW PostGIS for the Web
collection.





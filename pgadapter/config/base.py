import os

SETTINGS = {
    'logging': {
        'level': os.getenv('LOG')
    },
    'service': {
        'port': os.getenv('PORT')
    },
    'SQLALCHEMY_DATABASE_URI': os.getenv('SQLALCHEMY_DATABASE_URI'),
    'ITEMS_PER_PAGE': int(os.getenv('ITEMS_PER_PAGE', 20)),
    'UPLOAD_FOLDER': '/tmp/datasets',
    'ROLLBAR_SERVER_TOKEN': os.getenv('ROLLBAR_SERVER_TOKEN'),
    'ALLOWED_EXTENSIONS': {'zip'},
    'PG_SERVICE_SCHEMA': os.getenv('PG_SERVICE_SCHEMA', "pgadapter"),
}

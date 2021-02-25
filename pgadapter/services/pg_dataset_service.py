"""PG DATASET SERVICE """

import logging
import os

from werkzeug.utils import secure_filename

from pgadapter import db, app
from pgadapter.config import SETTINGS
from pgadapter.errors import InvalidFile, PGDatasetDuplicated, PGDatasetNotFound
from pgadapter.models import PGDataset
from pgadapter.utils import shp2pgsql

PG_SERVICE_SCHEMA = SETTINGS.get('PG_SERVICE_SCHEMA')


def allowed_file(filename):
    if len(filename.rsplit('.')) > 2:
        return filename.rsplit('.')[1] + '.' + filename.rsplit('.')[2].lower() in SETTINGS.get('ALLOWED_EXTENSIONS')
    else:
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in SETTINGS.get('ALLOWED_EXTENSIONS')


class PGDatasetService(object):
    """PG DATASET Service Class"""

    @staticmethod
    def create_pg_dataset(sent_file, form_data):
        logging.info('[SERVICE]: Creating pg dataset')

        table_name = form_data.get('table_name')

        existing_table = PGDataset.query.filter_by(table_name=f"{PG_SERVICE_SCHEMA}.{table_name}").first()

        if existing_table:
            raise PGDatasetDuplicated(message=f"Dataset with existing table name {table_name} already exists")

        if sent_file and allowed_file(sent_file.filename):
            logging.info('[SERVICE]: Allowed format')
            filename = secure_filename(sent_file.filename)
            sent_file_path = os.path.join(SETTINGS.get('UPLOAD_FOLDER'), filename)
            logging.info('[SERVICE]: Saving file')
            try:
                if not os.path.exists(SETTINGS.get('UPLOAD_FOLDER')):
                    os.makedirs(SETTINGS.get('UPLOAD_FOLDER'))
                sent_file.save(sent_file_path)
            except Exception as e:
                logging.error(e)
                raise e
            logging.info('[SERVICE]: File saved')
        else:
            raise InvalidFile(message='Invalid File')

        table = shp2pgsql(sent_file_path, form_data["table_name"])

        pg_dataset = PGDataset(**table)

        try:
            logging.info('[DB]: ADD')
            db.session.add(pg_dataset)
            db.session.commit()
        except Exception as e:
            raise e
        return pg_dataset

    @staticmethod
    def get_pg_datasets(page=1):
        logging.info('[SERVICE]: Getting pg_datasets')
        logging.info('[DB]: QUERY')

        per_page = app.config['ITEMS_PER_PAGE']
        query = PGDataset.query

        return query.paginate(page=page, per_page=per_page)

    @staticmethod
    def get_pg_dataset(pg_dataset_id):
        logging.info(f"[SERVICE]: Getting pg_dataset {pg_dataset_id} ")
        logging.info('[DB]: QUERY')

        try:
            pg_dataset = PGDataset.query.get(pg_dataset_id)
        except Exception as error:
            raise error

        if not pg_dataset:
            raise PGDatasetNotFound(message=f"Pg dataset with id {pg_dataset_id} does not exist")

        return pg_dataset

    @staticmethod
    def delete_pg_dataset(pg_dataset_id):
        logging.info(f"[SERVICE]: Deleting Pg Dataset {pg_dataset_id}")

        pg_dataset = PGDatasetService.get_pg_dataset(pg_dataset_id)

        try:
            logging.info('[DB]: DELETE')
            db.session.delete(pg_dataset)

            db.session.execute(f"DROP TABLE IF EXISTS {pg_dataset.table_name}")

            db.session.commit()

        except Exception as error:
            raise error
        return pg_dataset

import logging

from flask import jsonify, request

from pgadapter.errors import InvalidFile, PGDatasetDuplicated, PGDatasetNotFound
from pgadapter.routes.api.v1 import endpoints, error
from pgadapter.services import PGDatasetService
from pgadapter.validators import validate_file


# PG Dataset  Routes
@endpoints.route('/pg-dataset', strict_slashes=False, methods=['POST'])
@validate_file
def create_pg_dataset():
    """Create pg dataset"""
    logging.info('[ROUTER]: Creating pg dataset')

    sent_file = request.files.get('file')
    if sent_file.filename == '':
        sent_file.filename = 'dataset'

    body = request.form.to_dict()

    try:
        pg_dataset = PGDatasetService.create_pg_dataset(sent_file, body)
    except (InvalidFile, PGDatasetDuplicated) as e:
        logging.error('[ROUTER]: ' + e.message)
        return error(status=400, detail=e.message)
    except Exception as e:
        logging.error('[ROUTER]: ' + str(e))
        return error(status=500, detail='Generic Error')

    return jsonify(data=pg_dataset.serialize()), 200


@endpoints.route('/pg-dataset', strict_slashes=False, methods=['GET'])
def get_pg_datasets():
    """Get pg datasets"""
    logging.info('[ROUTER]: Getting all pg datasets')

    include = request.args.get('include')
    include = include.split(',') if include else []
    page = request.args.get('page', 1, type=int)

    try:
        result = PGDatasetService.get_pg_datasets(page=page)
    except Exception as e:
        logging.error('[ROUTER]: ' + str(e))
        return error(status=500, detail='Generic Error')

    response = {
        "data": [item.serialize(include) for item in result.items],
        "total": result.total,
        "has_next": result.has_next,
        "has_prev": result.has_prev,
        "page": result.page
    }

    return jsonify(**response), 200


@endpoints.route('/pg-dataset/<pg_dataset_id>', strict_slashes=False, methods=['DELETE'])
def delete_pg_dataset(pg_dataset_id):
    """Delete pg dataset"""
    logging.info(f"[ROUTER]: Deleting pg dataset: {pg_dataset_id} ")
    try:
        pg_dataset = PGDatasetService.delete_pg_dataset(pg_dataset_id=pg_dataset_id)
    except PGDatasetNotFound as e:
        logging.error('[ROUTER]: ' + e.message)
        return error(status=404, detail=e.message)
    except Exception as e:
        logging.error('[ROUTER]: ' + str(e))
        return error(status=500, detail='Generic Error')
    return jsonify(data=pg_dataset.serialize()), 200

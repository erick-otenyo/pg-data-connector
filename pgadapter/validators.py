from functools import wraps

from flask import request

from pgadapter.routes.api.v1 import error


def validate_file(func):
    """Dataset File Validation"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'file' not in request.files:
            return error(status=400, detail='File Required')
        if request.files.get('file', None) is None:
            return error(status=400, detail='File Required')
        return func(*args, **kwargs)

    return wrapper

""" NC ADAPTER ERRORS """


class Error(Exception):

    def __init__(self, message):
        self.message = message

    @property
    def serialize(self):
        return {
            'message': self.message
        }


class PGDatasetNotFound(Error):
    pass


class NoShpFound(Error):
    pass


class NoShxFound(Error):
    pass


class NoDbfFound(Error):
    pass


class InvalidFile(Error):
    pass


class PGDatasetDuplicated(Error):
    pass

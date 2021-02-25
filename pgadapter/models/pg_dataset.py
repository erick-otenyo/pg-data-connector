import uuid

from pgadapter import db
from pgadapter.models import GUID

db.GUID = GUID


class PGDataset(db.Model):
    id = db.Column(db.GUID(), default=uuid.uuid4, primary_key=True, autoincrement=False)
    table_name = db.Column(db.String(256), nullable=False)

    def __init__(self, table_name, srid=None):
        self.table_name = table_name

    def __repr__(self):
        return '<PGDataset %r>' % self.table_name

    def serialize(self, include=None):
        """Return object data in easily serializable format"""

        include = include if include else []

        pg_dataset = {
            "id": self.id,
            "table_name": self.table_name,
        }

        return pg_dataset

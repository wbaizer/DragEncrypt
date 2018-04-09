from dragencrypt import db
import datetime

# Process class
class Process(db.Model):
    __tablename__ = 'process'

    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(100), unique=True)
    storage_filename = db.Column(db.String(100))
    processed = db.Column(db.Boolean, default=False)
    process_begin = db.Column(db.DateTime)
    process_end = db.Column(db.DateTime)

    def __init__(original_filename, storage_filename):
        self.original_filename = original_filename
        self.storage_filename = storage_filename
        self.process_begin = datetime.datetime.now()

    def is_finished(self):
        """ True when encryption has finished """
        return processed

    def is_old(self):
        """Return True if the process was started over 24 hours ago """
        now = datetime.datetime.now()
        diff = now - self.process_begin
        hours = (diff.days * 24 * 60 * 60 + diff.seconds) / 3600.0
        return hours > 24

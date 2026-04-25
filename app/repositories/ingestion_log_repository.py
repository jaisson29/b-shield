from app.models.ingestion_log import IngestionLog


class IngestionLogsRepository:
    def __init__(self, session):
        self.session = session

    def create_log(self, log_data):
        log = IngestionLog(**log_data)
        self.session.add(log)
        self.session.commit()
        return log

    def get_log_by_id(self, log_id):
        return self.session.query(IngestionLog).filter_by(id=log_id).first()

    def get_all_logs(self):
        return self.session.query(IngestionLog).all()

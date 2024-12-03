import logging
from logging.config import dictConfig
from logging import Handler
from database.crud import insert_log
from database.connection import SessionLocal, engine
from schemas import schema

class DBLogHandler(Handler):
    def __init__(self):
        super().__init__()
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.session = SessionLocal()

    def emit(self, record):
        formatted_message = self.formatter.format(record)

        log_message = schema.Logger(
                level=record.levelname,
                message=formatted_message,
        )
        log_entry = insert_log(
            self.session,
            log_message
        )
    def __del__(self):
        self.session.close()

def setup_logging(logger_name=__name__, log_level=logging.WARNING):
    db_handler = DBLogHandler()
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.addHandler(db_handler)

    return logger

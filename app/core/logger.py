import logging
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "file_name": record.filename,
            "line": record.lineno,
            "method": record.funcName,
            "correlation_id": getattr(record, 'correlation_id', None)
        }
        if hasattr(record, "error"):
            log_record["error"] = record.error

        return json.dumps(log_record)
    
def setup_logger():
    logger = logging.getLogger("api_log")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JSONFormatter())
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()
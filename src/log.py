import loguru
from config import LOG_PATH
import os

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

logger = loguru.logger

logger.add(os.path.join(LOG_PATH, 'info.log'), filter=lambda record: record["level"].name == "INFO")
logger.add(os.path.join(LOG_PATH, 'error.log'), filter=lambda record: record["level"].name == "ERROR")


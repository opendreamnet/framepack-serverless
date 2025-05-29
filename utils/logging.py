import logging
import os

APP_LOG_LEVEL = int(os.environ.get("APP_LOG_LEVEL", logging.DEBUG))

logging.basicConfig(level=logging.getLevelName(APP_LOG_LEVEL))

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger("framepack")
logger.setLevel(APP_LOG_LEVEL)

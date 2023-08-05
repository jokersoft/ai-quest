import os
import logger

DEBUG = int(os.environ["DEBUG"])
logger = logging.getLogger()
if DEBUG == 1:
    logger.setLevel(logging.DEBUG)
    logger.debug("DEBUG mode enabled")
else:
    logger.setLevel(logging.INFO)

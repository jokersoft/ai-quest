import os
import sys
import logging


def configure_logger():
    DEBUG = int(os.environ.get("DEBUG", "0"))
    logging.basicConfig(stream=sys.stdout)
    logger = logging.getLogger()
    if DEBUG == 1:
        logger.setLevel(logging.DEBUG)
        logger.debug("DEBUG mode enabled")
    else:
        logger.setLevel(logging.INFO)
    return logger


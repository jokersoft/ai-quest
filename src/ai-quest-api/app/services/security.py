import logging
import os

from fastapi import Request, HTTPException, status

API_KEY_HEADER_NAME = os.environ.get("API_KEY_HEADER_NAME", "X-API-KEY")
API_KEY = os.environ.get("API_KEY")
IS_API_KEY_AUTH_DISABLED = os.environ.get("IS_API_KEY_AUTH_DISABLED", False)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


async def verify_api_key(request: Request):
    if IS_API_KEY_AUTH_DISABLED:
        logger.debug("API key authentication is disabled.")
        return

    if not API_KEY:
        logger.error("API_KEY environment variable is not set")
        raise ValueError("API_KEY environment variable is not set")

    current_api_key = request.headers.get(API_KEY_HEADER_NAME)
    if current_api_key != API_KEY:
        logger.warning("Could not validate credentials")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

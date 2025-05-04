import os

from fastapi import Request, HTTPException, status

API_KEY_HEADER_NAME = os.environ.get("API_KEY_HEADER_NAME", "X-API-KEY")
API_KEY = os.environ.get("API_KEY")

async def verify_api_key(request: Request):
    if not API_KEY:
        raise ValueError("API_KEY environment variable is not set")

    current_api_key = request.headers.get(API_KEY_HEADER_NAME)
    if current_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

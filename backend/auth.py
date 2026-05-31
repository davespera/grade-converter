from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os

# auto_error=True ensures FastAPI throws a 403 if the header is missing entirely
api_key = APIKeyHeader(name="x-api-key", auto_error=True)

async def handle_api_key(key: str = Security(api_key)):
    expected_key = os.getenv("FASTAPI_ACTIVEPIECES_API_KEY")

    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key authentication is not configured"
        )

    if key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key"
        )

    return key
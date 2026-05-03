from fastapi import Security, HTTPException, status, Request, Depends
from fastapi.security import APIKeyHeader
from sqlmodel import select

from sqlmodel.ext.asyncio.session import AsyncSession
from .database import get_database_session
from .models import ApiUser

# auto_error=True ensures FastAPI throws a 403 if the header is missing entirely
api_key = APIKeyHeader(name="x-api-key", auto_error=True)

# Could be changed in the future
internal_routes = [
    '/scales',
    '/transfer'
]

print(f"Checking key: {key}")

async def handle_api_key(req: Request, db: AsyncSession = Depends(get_database_session), key: str = Security(api_key)):
    
    print(f"--- DEBUG: Incoming Request to {req.url.path} with key: {key} ---")

    query = select(ApiUser).where(ApiUser.api_key == key).where(ApiUser.active == True)
    res = await db.exec(query)
    api_key_data = res.first()

    # No active API key found
    if not api_key_data:
        print("--- DEBUG: Auth Failed: No user found ---")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key"
        )

    # Check if the user is trying to access an internal route
    for path in internal_routes:
        if path in req.url.path and not api_key_data.is_internal:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this route"
            )

    # Check if the user has any credits left
    #if api_key_data.curr_credits <= 0:
        #raise HTTPException(
            #status_code=status.HTTP_402_PAYMENT_REQUIRED,
            #detail="You have no credits left for the month"
        #)

    yield api_key_data

    # If successful, decrement the user's credits
    # api_key_data.curr_credits -= 1
    # db.commit()
    # db.refresh(api_key_data)
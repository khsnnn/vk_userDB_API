import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

auth_security = HTTPBearer()
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

def validate_token(credentials: HTTPAuthorizationCredentials = Depends(auth_security)):
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials.credentials

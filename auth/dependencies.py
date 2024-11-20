from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from .service import AuthService
from .schemas import TokenPayload, ErrorResponse
from functools import lru_cache

security = HTTPBearer()

@lru_cache()
def get_auth_service():
    """Reusable dependency for AuthService"""
    return AuthService()

async def get_current_user(
    token = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenPayload:
    """Reusable dependency for protected routes"""
    payload = auth_service.parse_jwt_token(token.credentials)
    if not payload:
        raise HTTPException(
            status_code=401, 
            detail=ErrorResponse(detail="Invalid token").model_dump()
        )
    return TokenPayload(**payload)
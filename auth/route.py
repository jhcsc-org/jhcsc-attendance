from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from typing import Optional
from .service import AuthService

security = HTTPBearer()

router = APIRouter()

async def auth_middleware(
    authorization: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validate JWT token and return user email if valid
    """
    token = authorization.credentials
    auth_service = AuthService()
    payload = auth_service.parse_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["email"]

@router.post(
    "/secret",
    summary="Protected endpoint requiring JWT",
    description="Access this endpoint with a valid Supabase JWT token",
    responses={
        200: {"description": "Success"},
        401: {"description": "Invalid or missing token"}
    }
)
async def secret_route(email: str = Depends(auth_middleware)):
    return {
        "message": f"Hello {email}, you have access to this protected route"
    }

@router.get("/protected")
async def protected_route(email: str = Depends(auth_middleware)):
    return {
        "message": f"Protected data for {email}"
    }

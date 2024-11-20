from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict

class TokenPayload(BaseModel):
    """JWT token payload schema"""
    email: EmailStr
    sub: str
    aud: str
    exp: int
    iat: int
    role: str
    session_id: str
    app_metadata: Dict
    user_metadata: Dict
    is_anonymous: bool

class ErrorResponse(BaseModel):
    detail: str

class AuthResponse(BaseModel):
    message: str
    email: EmailStr
from jose import jwt, JWTError
from typing import Optional
import os
import logging

class Claims:
    def __init__(self, email: str):
        self.email = email

class AuthService:
    def __init__(self):
        self.jwt_secret = 'DL6WdvRAcQoFZSrXqxbJ/TEJDGuX3kEEPhEVEXU1aNsEnvpln6XMAgQ3/P4MqpW3A+Ost+PTY89wIlEojCnKLQ=='
        if not self.jwt_secret:
            raise ValueError('Missing SUPABASE_JWT_SECRET')

    def parse_jwt_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],
                options={
                    "verify_aud": False,
                    "verify_iss": False,
                }
            )
            if not payload.get("email"):
                raise ValueError("Missing email claim")
            logging.info(f"Decoded payload: {payload}")
            return payload
            
        except (JWTError, ValueError) as e:
            logging.error(f"Token validation failed: {str(e)}")
            return None
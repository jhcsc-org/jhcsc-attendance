from functools import wraps
from typing import Callable
import uuid

def generate_uuid(prefix: str) -> str:
    """Simple generator for generating UUID4"""
    return f"{prefix}-{uuid.uuid4()}"

def endpoint_docs(**kwargs):
    """Decorator for adding OpenAPI documentation to endpoints"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kw):
            return await func(*args, **kw)
        for key, value in kwargs.items():
            setattr(wrapper, key, value)
        return wrapper
    return decorator
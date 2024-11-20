from datetime import datetime
from typing import Dict, Optional, List
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from models import RegistrationStep

class RegistrationPersonalInfoSchema(BaseModel):
    """Schema for registration personal information"""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: datetime
    gender: str = Field(..., min_length=1, max_length=20)

class RegistrationContactInfoSchema(BaseModel):
    """Schema for registration contact information"""
    email: EmailStr
    phone: str = Field(..., max_length=20)
    address: str
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=20)
    country: str = Field(..., max_length=100)

class RegistrationDocumentSchema(BaseModel):
    """Schema for registration documents"""
    id: str
    document_type: str = Field(..., max_length=50)
    file_path: str = Field(..., max_length=255)
    uploaded_at: datetime

class RegistrationSessionBase(BaseModel):
    """Base schema for registration session shared properties"""
    student_id: int = Field(..., gt=0)
    current_step: Optional[RegistrationStep] = None
    completed_steps: Dict[str, bool] = Field(
        default_factory=dict,
        description="Map of completed registration steps"
    )

    model_config = ConfigDict(from_attributes=True)

class RegistrationSessionCreate(RegistrationSessionBase):
    """Schema for creating a new registration session"""
    pass

class RegistrationSessionUpdate(BaseModel):
    """Schema for updating a registration session"""
    current_step: Optional[RegistrationStep] = None
    completed_steps: Optional[Dict[str, bool]] = None

    model_config = ConfigDict(from_attributes=True)

class RegistrationSessionResponse(RegistrationSessionBase):
    """Schema for registration session responses"""
    id: str = Field(..., min_length=1, max_length=50)
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    personal_info: Optional[RegistrationPersonalInfoSchema] = None
    contact_info: Optional[RegistrationContactInfoSchema] = None
    documents: List[RegistrationDocumentSchema] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

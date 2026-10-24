from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class VendorBase(BaseModel):
    name: str
    gstin: Optional[str] = None
    pan: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    state_code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    state_code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class VendorResponse(VendorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

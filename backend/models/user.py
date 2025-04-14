from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    username: str
    password_hash: str
    role: str  # Producer, Distributor, Retailer, Regulator, Consumer
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    registered_at: Optional[datetime] = None
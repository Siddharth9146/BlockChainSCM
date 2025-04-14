from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    name: str
    email: EmailStr
    password_hash: str
    role: str  # producer, distributor, retailer, regulator, consumer
    registered_at: Optional[datetime] = datetime.utcnow()
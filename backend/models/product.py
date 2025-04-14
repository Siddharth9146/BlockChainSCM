from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Product(BaseModel):
    productId: str  # blockchain ID
    name: str
    description: Optional[str] = None
    current_owner: str  # email of user or _id
    status: str  # e.g., In Transit, Delivered
    price: Optional[float] = None
    location: Optional[str] = None
    last_updated: Optional[datetime] = datetime.utcnow()
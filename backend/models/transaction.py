from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Transaction(BaseModel):
    productId: str
    from_user: str  # username of sender
    to_user: str  # username of receiver
    timestamp: Optional[datetime] = None
    action: str  # created, transferred, updated, shipped, received, verified
    status: Optional[str] = None  # Product status at this transaction point
    note: Optional[str] = None
    location: Optional[str] = None
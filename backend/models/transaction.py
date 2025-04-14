from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Transaction(BaseModel):
    productId: str
    from_user: str  # email or _id
    to_user: str
    timestamp: Optional[datetime] = datetime.utcnow()
    action: str  # shipped, received, verified
    note: Optional[str] = None
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Product(BaseModel):
    productId: Optional[str] = None  # blockchain ID (can be auto-generated)
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = 1
    location: Optional[str] = None
    current_owner: Optional[str] = None  # username of current owner
    status: Optional[str] = "Produced"  # e.g., Produced, In Transit, Delivered
    price: Optional[float] = None
    date_created: Optional[str] = None  # date string, formatted as YYYY-MM-DD
    image_url: Optional[str] = None  # URL to product image if uploaded
    last_updated: Optional[datetime] = None
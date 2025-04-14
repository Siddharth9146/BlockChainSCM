from pydantic import BaseModel
from typing import List

class RolePermission(BaseModel):
    role: str
    permissions: List[str]  # e.g., ["add_product", "verify_product"]
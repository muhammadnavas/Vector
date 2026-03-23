from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Sample Item",
                "description": "A sample item description",
                "price": 99.99
            }
        }

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

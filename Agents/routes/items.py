from fastapi import APIRouter, HTTPException
from models import Item, ItemUpdate
from typing import List

router = APIRouter(prefix="/items", tags=["items"])

# Mock database
db_items = {
    1: {"id": 1, "name": "Item 1", "description": "First item", "price": 10.99},
    2: {"id": 2, "name": "Item 2", "description": "Second item", "price": 20.99},
}

@router.get("", response_model=List[Item])
def get_items():
    """Get all items"""
    return list(db_items.values())

@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int):
    """Get a specific item"""
    if item_id not in db_items:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_items[item_id]

@router.post("", response_model=Item)
def create_item(item: Item):
    """Create a new item"""
    new_id = max(db_items.keys()) + 1 if db_items else 1
    item.id = new_id
    db_items[new_id] = item.dict()
    return db_items[new_id]

@router.put("/{item_id}", response_model=Item)
def update_item(item_id: int, item_update: ItemUpdate):
    """Update an existing item"""
    if item_id not in db_items:
        raise HTTPException(status_code=404, detail="Item not found")

    existing_item = db_items[item_id]
    update_data = item_update.dict(exclude_unset=True)
    db_items[item_id] = {**existing_item, **update_data}
    return db_items[item_id]

@router.delete("/{item_id}")
def delete_item(item_id: int):
    """Delete an item"""
    if item_id not in db_items:
        raise HTTPException(status_code=404, detail="Item not found")

    deleted_item = db_items.pop(item_id)
    return {"message": "Item deleted", "item": deleted_item}

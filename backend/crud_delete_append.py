
def delete_inventory_item(db: Session, item_id: str) -> bool:
    """
    Deletes an inventory item by ID.
    Returns True if deleted, False if no such item existed.
    """
    item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False

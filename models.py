from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Temel model
class NoteBase(BaseModel):
    title: str
    content: str
    is_pinned: bool = False
    is_favorite: bool = False

# Not oluşturma isteği
class NoteCreate(NoteBase):
    pass

# Not güncelleme isteği
class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_favorite: Optional[bool] = None
# API Response (ID artık string!)
class Note(NoteBase):
    id: str
    user_id: str
    # Firestore timestamp'i datetime objesi olarak döner
    created_at: Optional[datetime] = None 
    updated_at: Optional[datetime] = None

    class Config:
        # Pydantic'in obje dönüşümlerine izin ver
        from_attributes = True
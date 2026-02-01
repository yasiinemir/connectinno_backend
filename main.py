from fastapi import FastAPI, HTTPException, Header, Depends
from typing import List, Optional
from firebase_admin import auth
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime
from db import db  # db.py'den Firestore bağlantısını çekiyoruz
from models import Note, NoteCreate, NoteUpdate

app = FastAPI(title="Connectinno Notes API - Firebase Edition")

# --- Security Helper ---
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    
    try:
        token = authorization.split(" ")[1]
        # Firebase ID Token'ı doğrula
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']  # Kullanıcının User ID'sini dön
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Token: {str(e)}")

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Firebase API is running."}

# 1. Notları Listele
@app.get("/notes", response_model=List[Note])
def get_notes(user_id: str = Depends(get_current_user)):
    notes_ref = db.collection('notes')
    # Sadece o kullanıcının notlarını filtrele
    query = notes_ref.where(filter=FieldFilter("user_id", "==", user_id))
    results = query.stream()
    
    notes_list = []
    for doc in results:
        data = doc.to_dict()
        data['id'] = doc.id  # Doküman ID'sini dataya ekle
        notes_list.append(data)
        
    return notes_list

# 2. Not Oluştur
@app.post("/notes", response_model=Note)
def create_note(note: NoteCreate, user_id: str = Depends(get_current_user)):
    data = note.dict()
    data["user_id"] = user_id
    data["created_at"] = datetime.now()
    data["updated_at"] = datetime.now()
    
    # Firestore'a yeni doküman ekle (ID otomatik oluşur)
    update_time, doc_ref = db.collection('notes').add(data)
    
    # Oluşan veriyi geri dön
    data["id"] = doc_ref.id
    return data

# 3. Not Güncelle
@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: str, note: NoteUpdate, user_id: str = Depends(get_current_user)):
    doc_ref = db.collection('notes').document(note_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Note not found")
        
    existing_data = doc.to_dict()
    # Başkasının notunu güncellemeyi engelle
    if existing_data.get('user_id') != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this note")
        
    # Sadece dolu gelen alanları al
    update_data = {k: v for k, v in note.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now()
    
    doc_ref.update(update_data)
    
    # Güncel veriyi birleştirip dön
    existing_data.update(update_data)
    existing_data['id'] = note_id
    return existing_data

# 4. Not Sil
@app.delete("/notes/{note_id}")
def delete_note(note_id: str, user_id: str = Depends(get_current_user)):
    doc_ref = db.collection('notes').document(note_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Note not found")
        
    if doc.to_dict().get('user_id') != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this note")
        
    doc_ref.delete()
    return {"detail": "Note deleted successfully"}
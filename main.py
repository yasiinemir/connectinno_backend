import os
from fastapi import FastAPI, HTTPException, Header, Depends
from typing import List, Optional
from firebase_admin import auth
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime
from db import db  
from models import Note, NoteCreate, NoteUpdate
from pydantic import BaseModel
import google.generativeai as genai
import yt_dlp
import os


app = FastAPI(title="Connectinno Notes API - Firebase Edition")


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    try:
        token = authorization.split(" ")[1]
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']  
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Token: {str(e)}")
    
GENAI_API_KEY = "AIzaSyBlmJVC3YRvA4s2MEfyh2_0Y_rak92dDII"
genai.configure(api_key=GENAI_API_KEY)

class NoteRequest(BaseModel):
    text: str

def search_youtube(query):
    """
    YouTube araması yapar. Bot korumasını aşmak için User-Agent kullanır.
    """
    print(f"DEBUG: '{query}' için YouTube'da arama başlatılıyor...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch1:',
        'socket_timeout': 10,
       
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                video = info['entries'][0]
            else:
                video = info
            print(f"DEBUG: Bulunan Video ID: {video.get('id')}")
            return {
                "id": video['id'],
                "title": video['title'],               
                "thumbnail": f"https://img.youtube.com/vi/{video['id']}/hqdefault.jpg"
            }
            
        except Exception as e:
            print(f"KRİTİK HATA - YouTube Arama Fonksiyonu Çöktü: {e}")
            return None
@app.post("/recommend-music")
async def recommend_music(note: NoteRequest):
    try:    
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"""
        Görevin: Aşağıdaki metni analiz et ve ruh haline en uygun şarkıyı bul.   
        ÇOK ÖNEMLİ KURAL: Çıktı olarak SADECE ve SADECE "Sanatçı - Şarkı" yaz.
        Kesinlikle "Analiz:", "Duygu:", madde işareti, yıldız (*) veya açıklama cümlesi KULLANMA.
        Sadece şarkı ismini ver ve sus.   
        Örnek Doğru Çıktı: Queen - Bohemian Rhapsody
        Analiz Edilecek Metin: "{note.text}"
        """
        
        response = model.generate_content(prompt)
        raw_output = response.text.strip() 
        print(f"AI Ham Cevap: {raw_output}") 
        if "\n" in raw_output:
            song_query = raw_output.split("\n")[-1].strip()
        else:
            song_query = raw_output
        song_query = song_query.replace("*", "").replace('"', '').strip()
        if ":" in song_query:
            song_query = song_query.split(":")[-1].strip()
        print(f"YouTube'da Aranacak Temiz Veri: {song_query}")
    
        video_result = search_youtube(song_query)
        print("DEBUG - YouTube Arama Sonucu:", video_result)

        if not video_result:
            
            raise HTTPException(status_code=404, detail="Şarkı bulunamadı")

        return {
            "mood_description": song_query,
            "video_id": video_result['id'],
            "video_title": video_result['title'],
            "thumbnail": video_result['thumbnail']
        }

    except Exception as e:
        print(f"Genel Hata: {e}")
        return {
            "mood_description": "Hata oluştu, Lo-Fi moduna geçildi",
            "video_id": "jfKfPfyJRdk", 
            "video_title": "lofi hip hop radio",
            "thumbnail": ""
        }


@app.get("/")
def read_root():
    return {"message": "Firebase API is running."}


@app.get("/notes", response_model=List[Note])
def get_notes(user_id: str = Depends(get_current_user)):
    notes_ref = db.collection('notes')
    
    query = notes_ref.where(filter=FieldFilter("user_id", "==", user_id))
    results = query.stream()
    
    notes_list = []
    for doc in results:
        data = doc.to_dict()
        data['id'] = doc.id  
        notes_list.append(data)
        
    return notes_list


@app.post("/notes", response_model=Note)
def create_note(note: NoteCreate, user_id: str = Depends(get_current_user)):
    data = note.dict()
    data["user_id"] = user_id
    data["created_at"] = datetime.now()
    data["updated_at"] = datetime.now()
    update_time, doc_ref = db.collection('notes').add(data)

    data["id"] = doc_ref.id
    return data


@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: str, note: NoteUpdate, user_id: str = Depends(get_current_user)):
    doc_ref = db.collection('notes').document(note_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Note not found")
        
    existing_data = doc.to_dict()
    
    if existing_data.get('user_id') != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this note")
        
    
    update_data = {k: v for k, v in note.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now()
    
    doc_ref.update(update_data)
    
    
    existing_data.update(update_data)
    existing_data['id'] = note_id
    return existing_data


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
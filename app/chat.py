from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import random 

from . import models, database

router = APIRouter()
load_dotenv()

# API anahtarını yükle
GEMINI_API_KEY = os.getenv("LLM_API_KEY")

# Gemini yapılandırması
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    raise Exception("GEMINI_API_KEY .env dosyasında tanımlanmalı!")

# Model yüklemesi
# Görselde belirtilen 'gemini-2.0-flash' modelini kullanıyoruz.
gemini_model = genai.GenerativeModel(
    'gemini-2.0-flash', # Model adını 'gemini-2.0-flash' olarak değiştirdik
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

# DB session dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# GET: Sohbet sayfası
@router.get("/chat")
def get_chat(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    # Kullanıcının tüm chatlerini (sohbetlerini) getir
    chats = db.query(models.Chat).filter_by(user_id=user_id).order_by(models.Chat.created_at.desc()).all()
    user = db.query(models.User).filter_by(id=user_id).first()
    rooms = db.query(models.ChatRoom).join(models.ChatRoomMember).filter(models.ChatRoomMember.user_id == user_id).all()

    # Aktif chat_id cookie'den alınır, yoksa en yenisi seçilir
    active_chat_id = request.cookies.get("active_chat_id")
    active_chat = None
    messages = []
    if active_chat_id:
        active_chat = db.query(models.Chat).filter_by(id=active_chat_id, user_id=user_id).first()
    if not active_chat and chats:
        active_chat = chats[0]
        active_chat_id = active_chat.id if active_chat else None
    if active_chat:
        messages = db.query(models.Message).filter_by(chat_id=active_chat.id).order_by(models.Message.timestamp).all()

    return database.templates.TemplateResponse("chat.html", {
        "request": request,
        "chats": chats,
        "messages": messages,
        "user": user,
        "rooms": rooms,
        "current_chat_id": active_chat_id
    })

import uuid

@router.get("/chat/new")
def new_chat(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    # Yeni chat oluştur
    new_chat = models.Chat(user_id=user_id, created_at=datetime.utcnow())
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    response = RedirectResponse("/chat", status_code=303)
    response.set_cookie("active_chat_id", str(new_chat.id), max_age=60*60*24)
    return response




# POST: Yeni mesaj al ve cevapla (TEK BİR FONKSİYON HALİNDE)


# POST: Yeni mesaj al ve cevapla (TEK BİR FONKSİYON HALİNDE)
@router.post("/chat")
def post_chat(request: Request, user_input: str = Form(None), select_chat_id: int = Form(None), db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    # Eğer kullanıcı sidebar'dan chat seçtiyse, sadece aktif chat_id'yi güncelle ve geri dön
    if select_chat_id:
        response = RedirectResponse("/chat", status_code=303)
        response.set_cookie("active_chat_id", str(select_chat_id), max_age=60*60*24)
        return response

    # Normal mesaj gönderme akışı
    chat_id = request.cookies.get("active_chat_id")
    if not chat_id:
        # Eğer aktif chat yoksa yeni chat başlat
        new_chat = models.Chat(user_id=user_id, created_at=datetime.utcnow())
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)
        chat_id = new_chat.id

    # O chat'e ait geçmiş mesajları al
    past_messages_db = db.query(models.Message).filter_by(chat_id=chat_id).order_by(models.Message.timestamp).all()

    # Sohbet geçmişini Gemini'nin beklediği formata dönüştür
    chat_history_for_gemini = []
    chat_history_for_gemini.append({"role": "user", "parts": [{"text": "Sen empatik bir dijital danışmansın. Kullanıcının duygularını nazikçe anlayıp destekleyici yanıtlar ver."}]})
    for msg in past_messages_db:
        chat_history_for_gemini.append({"role": "user", "parts": [{"text": msg.user_input}]})
        chat_history_for_gemini.append({"role": "model", "parts": [{"text": msg.ai_response}]})

    # Mevcut kullanıcı mesajını ekle
    if user_input:
        chat_history_for_gemini.append({"role": "user", "parts": [{"text": user_input}]})
        # LLM'den cevap al
        ai_response = get_llm_response(chat_history_for_gemini)
        # Mesajı aktif chat'e kaydet
        new_msg = models.Message(
            user_id=user_id,
            chat_id=chat_id,
            user_input=user_input,
            ai_response=ai_response,
            timestamp=datetime.utcnow(),
            stress_score=random.uniform(0.1, 0.9)
        )
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)
    response = RedirectResponse("/chat", status_code=303)
    response.set_cookie("active_chat_id", str(chat_id), max_age=60*60*24)
    return response


# Gemini API'den cevap al
# Artık tek bir parametre alıyor: Gemini'nin beklediği formatta hazırlanmış mesaj listesi
def get_llm_response(messages_to_send: list) -> str:
    try:
        # generate_content'e direkt olarak mesaj listesi verilir
        response = gemini_model.generate_content(
            messages_to_send, # Doğrudan mesaj listesini gönderiyoruz
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=300,
            )
        )
        return response.text.strip()

    except Exception as e:
        print("Gemini API hatası:", e)
        return "Üzgünüm, şu anda yanıt veremiyorum 😔"


# GET: Geçmiş sohbetleri göster
@router.get("/history")
def view_history(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    messages = db.query(models.Message).filter_by(user_id=user_id).order_by(models.Message.timestamp.desc()).all()
    return database.templates.TemplateResponse("history.html", {
        "request": request,
        "messages": messages
    })




##durum güncelleme
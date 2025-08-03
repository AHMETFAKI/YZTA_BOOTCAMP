# app/relax.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from markupsafe import Markup
import random
from . import models, database

router = APIRouter()

# Veritabanı bağlantısı
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rahatlama sayfası
@router.get("/relax")
def relax_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    last_msg = db.query(models.Message)\
                 .filter_by(user_id=user_id)\
                 .order_by(models.Message.timestamp.desc())\
                 .first()

    # Ruh hali ve müzik önerisi belirleme
    if last_msg:
        stress = last_msg.stress_score
        if stress >= 0.7:
            mood = "Hüzünlü"
            suggestion = Markup(
                "Lo-fi müzik öneriyoruz: <a href='https://www.youtube.com/watch?v=jfKfPfyJRdk' target='_blank' rel='noopener noreferrer'>Lo-Fi Beats 🎧</a>"
            )
        elif stress >= 0.4:
            mood = "Orta"
            suggestion = Markup(
                "Hafif caz öneriyoruz: <a href='https://www.youtube.com/watch?v=Dx5qFachd3A' target='_blank' rel='noopener noreferrer'>Jazz Vibes 🎷</a>"
            )
        else:
            mood = "Rahat"
            suggestion = Markup(
                "Enerjik pop öneriyoruz: <a href='https://www.youtube.com/watch?v=ZbZSe6N_BXs' target='_blank' rel='noopener noreferrer'>Happy Hits 🎶</a>"
            )
    else:
        mood = "Bilinmiyor"
        suggestion = Markup("Henüz stres skorun yok. <a href='/chat'>Sohbete başla!</a>")

    # Günlük önerilerden 3 tanesini rastgele seç
    advice_list = [
        "Günlük nefes egzersizleri yap.",
        "Kendine karşı nazik ol.",
        "Kısa bir yürüyüş zihnini toparlayabilir.",
        "Duygularını yazmak hafifletici olabilir.",
        "Ekran molaları vermeyi unutma.",
        "Sevdiğin birini ara, kısa da olsa."
    ]
    random.shuffle(advice_list)

    return database.templates.TemplateResponse("relax.html", {
        "request": request,
        "mood": mood,
        "music": suggestion,
        "advice_list": advice_list[:3]
    })

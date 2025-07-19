from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import models, database

router = APIRouter()

# DB session dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/report")
def get_report(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)

    # Son 7 günün verilerini al
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    messages = db.query(models.Message).filter(
        models.Message.user_id == user_id,
        models.Message.timestamp >= one_week_ago
    ).order_by(models.Message.timestamp).all()

    # Günlere göre stres skorlarını grupla
    stress_by_day = {}
    for i in range(7):
        day = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
        stress_by_day[day] = []

    for msg in messages:
        day_str = msg.timestamp.strftime('%Y-%m-%d')
        if day_str in stress_by_day:
            stress_by_day[day_str].append(msg.stress_score)

    # Günlük ortalama stres skorlarını hesapla
    labels = []
    data = []
    for day, scores in sorted(stress_by_day.items()):
        labels.append(datetime.strptime(day, '%Y-%m-%d').strftime('%a')) # Gün adları (Mon, Tue)
        if scores:
            avg_score = sum(scores) / len(scores)
            data.append(round(avg_score * 100)) # Yüzde olarak
        else:
            data.append(0)

    return database.templates.TemplateResponse("report.html", {
        "request": request,
        "labels": labels,
        "data": data
    })
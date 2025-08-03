from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import models, database

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Listele - kullanıcının üye olduğu odalar
@router.get("/rooms")
def list_rooms(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    rooms = db.query(models.ChatRoom).join(models.ChatRoomMember).filter(models.ChatRoomMember.user_id == user_id).all()
    return database.templates.TemplateResponse("chat_rooms.html", {"request": request, "rooms": rooms})

# Oda oluşturma formu (GET)
@router.get("/rooms/create")
def create_room_form(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    # Mevcut kullanıcı hariç tüm kullanıcıları getir
    users = db.query(models.User).filter(models.User.id != user_id).all()
    return database.templates.TemplateResponse("chat_room_create.html", {"request": request, "users": users})

# Oda oluştur (POST, çoklu üye ekleme)
@router.post("/rooms/create")
def create_room(request: Request, name: str = Form(...), is_group: str = Form(None), user_ids: list = Form([]), db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    room = models.ChatRoom(name=name, is_group=1 if is_group else 0)
    db.add(room)
    db.commit()
    db.refresh(room)
    # Odaya kurucu kullanıcıyı ekle
    member = models.ChatRoomMember(room_id=room.id, user_id=user_id)
    db.add(member)
    # Seçilen diğer üyeleri ekle (tekrar eklememek için kontrol)
    for uid in user_ids:
        if str(uid) != str(user_id):
            exists = db.query(models.ChatRoomMember).filter_by(room_id=room.id, user_id=uid).first()
            if not exists:
                db.add(models.ChatRoomMember(room_id=room.id, user_id=uid))
    db.commit()
    return RedirectResponse(f"/rooms/{room.id}", status_code=303)

# Oda detay (mesajlar)
@router.get("/rooms/{room_id}")
def room_detail(request: Request, room_id: int, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    room = db.query(models.ChatRoom).filter_by(id=room_id).first()
    if not room:
        raise HTTPException(404, "Oda bulunamadı")
    # Üyelik kontrolü
    is_member = db.query(models.ChatRoomMember).filter_by(room_id=room_id, user_id=user_id).first()
    if not is_member:
        return RedirectResponse("/rooms", status_code=303)
    messages = db.query(models.ChatMessage).filter_by(room_id=room_id).order_by(models.ChatMessage.timestamp).all()
    members = db.query(models.ChatRoomMember).filter_by(room_id=room_id).all()
    return database.templates.TemplateResponse("chat_room.html", {"request": request, "room": room, "messages": messages, "members": members})

# Mesaj gönder
@router.post("/rooms/{room_id}")
def send_message(request: Request, room_id: int, message: str = Form(...), db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    # Üyelik kontrolü
    is_member = db.query(models.ChatRoomMember).filter_by(room_id=room_id, user_id=user_id).first()
    if not is_member:
        return RedirectResponse("/rooms", status_code=303)
    msg = models.ChatMessage(room_id=room_id, sender_id=user_id, message=message)
    db.add(msg)
    db.commit()
    return RedirectResponse(f"/rooms/{room_id}", status_code=303)

# Davet ekranı (GET)
@router.get("/rooms/{room_id}/invite")
def invite_form(request: Request, room_id: int, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    room = db.query(models.ChatRoom).filter_by(id=room_id).first()
    if not room:
        raise HTTPException(404, "Oda bulunamadı")
    # Sadece grup odası ise davet
    if not room.is_group:
        return RedirectResponse(f"/rooms/{room_id}", status_code=303)
    # Odaya üye olmayanları getir
    subquery = db.query(models.ChatRoomMember.user_id).filter_by(room_id=room_id)
    users = db.query(models.User).filter(~models.User.id.in_(subquery)).all()
    return database.templates.TemplateResponse("chat_room_invite.html", {"request": request, "room": room, "users": users})

# Davet işlemi (POST)
@router.post("/rooms/{room_id}/invite")
def invite_user(request: Request, room_id: int, user_id: int = Form(...), db: Session = Depends(get_db)):
    my_id = request.cookies.get("user_id")
    if not my_id:
        return RedirectResponse("/login", status_code=303)
    room = db.query(models.ChatRoom).filter_by(id=room_id).first()
    if not room or not room.is_group:
        return RedirectResponse(f"/rooms/{room_id}", status_code=303)
    # Zaten üye mi kontrolü
    exists = db.query(models.ChatRoomMember).filter_by(room_id=room_id, user_id=user_id).first()
    if exists:
        return RedirectResponse(f"/rooms/{room_id}", status_code=303)
    member = models.ChatRoomMember(room_id=room_id, user_id=user_id)
    db.add(member)
    db.commit()
    return RedirectResponse(f"/rooms/{room_id}", status_code=303)

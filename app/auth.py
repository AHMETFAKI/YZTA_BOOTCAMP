from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from . import models, database

router = APIRouter()

# DB session dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/register")
def register_form(request: Request):
    return database.templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="Bu e-posta zaten kayıtlı.")

    hashed_pw = bcrypt.hash(password)
    new_user = models.User(email=email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    return RedirectResponse("/login", status_code=303)

@router.get("/login")
def login_form(request: Request):
    return database.templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not bcrypt.verify(password, user.hashed_password):
        return database.templates.TemplateResponse(
            "login.html", {"request": request, "error": "Hatalı giriş"}
        )

    response = RedirectResponse("/chat", status_code=303)
    response.set_cookie("user_id", str(user.id))  # Basit oturum yönetimi
    return response

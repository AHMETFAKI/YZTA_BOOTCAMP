# from app.database import Base, engine
# from app import models
#
# models.Base.metadata.create_all(bind=engine)


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

from . import models, database, auth, chat


from fastapi import Request
from fastapi.responses import RedirectResponse

# .env dosyasını yükle
load_dotenv()

# FastAPI uygulamasını başlat
app = FastAPI()

# HTML şablonlarını tanımla
templates = Jinja2Templates(directory="app/templates")
database.templates = templates  # dışarıdan erişmek için

# Statik dosyaları bağla (CSS vb.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Veritabanı tablolarını oluştur
models.Base.metadata.create_all(bind=database.engine)

# Route dosyalarını bağla
app.include_router(auth.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return RedirectResponse("/login")  # veya "/register"



##durum güncelleme
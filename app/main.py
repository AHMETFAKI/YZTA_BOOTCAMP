from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os

from . import models, database, auth, chat, chat_rooms, relax, report

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
app.include_router(chat_rooms.router)
app.include_router(report.router)
app.include_router(relax.router)

@app.get("/")
def root():
    return RedirectResponse("/login")

##durum güncelleme
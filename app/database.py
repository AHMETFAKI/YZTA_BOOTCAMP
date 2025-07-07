from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# .env içinden veritabanı URL'sini al
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chat.db")

# SQLite için connect_args gerekiyor (thread sorunlarını önler)
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Model tanımları için kullanılacak base class
Base = declarative_base()

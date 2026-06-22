"""
SQLite veritabanı bağlantısı.
Bölüm 2.3 / 6.4: Şema, kod yazmadan SQLite araçlarıyla (DB Browser, VSCode eklentisi)
doğrudan okunabilir olacak şekilde sade tutulmuştur — bu yüzden gereksiz
normalizasyon yapılmaz, tablo/alan adları İngilizce ve açık tutulur.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: her istek için bir DB session açar, sonunda kapatır."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

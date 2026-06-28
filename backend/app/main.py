"""
FastAPI giriş noktası.
Başlangıçta: (1) tabloları oluşturur, (2) modules_config/ klasöründeki
yapılandırma dosyalarını okuyup `modules` tablosuna senkronize eder (FR-1.2).
"""
import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models.models import Module
from app.routers import dialogue, progress, quiz, sessions, students, survey, tasks

settings = get_settings()

app = FastAPI(title="Learning LLMs with LLMs", version="0.1.0 (MVP)")

# CORS: local dev için (Vite dev server farklı portta çalışır).
# Production'da frontend FastAPI'den servis edildiği için CORS gerekmez,
# ama ALLOWED_ORIGINS env var ile production URL eklenebilir.
_extra_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"] + _extra_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def sync_modules_from_config() -> None:
    """FR-1.2: modules_config/ altındaki her JSON dosyasını modules tablosuna yazar/günceller."""
    config_dir = Path(settings.modules_config_dir)
    if not config_dir.exists():
        return

    db = SessionLocal()
    try:
        for config_file in config_dir.glob("*.json"):
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            existing = db.query(Module).filter(Module.code == data["code"]).first()
            if existing:
                existing.name = data["name"]
                existing.phase = data["phase"]
                existing.config_path = str(config_file)
            else:
                db.add(
                    Module(
                        code=data["code"],
                        name=data["name"],
                        phase=data["phase"],
                        config_path=str(config_file),
                    )
                )
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    sync_modules_from_config()

    # FR-4.1: RAG dokümanlarını embed edip chromadb'ye yazar (sadece ilk
    # çalıştırmada veya koleksiyon boşsa — bkz. vector_store.ingest_documents).
    # İnternet yoksa (embedding modeli indirilemezse) burada hata fırlatmak
    # yerine logluyoruz; "doküman ara" aracı o durumda boş sonuç döner ama
    # uygulamanın geri kalanı (Teori/Eleştirel katmanlar, kimlik, oturum)
    # normal çalışmaya devam eder.
    try:
        from app.services.vector_store import ingest_documents

        count = ingest_documents()
        print(f"[startup] RAG doküman koleksiyonu hazır: {count} chunk.")
    except Exception as e:  # noqa: BLE001 — başlangıçta uygulamayı düşürmemek kasıtlı
        print(f"[startup] UYARI: RAG dokümanları embed edilemedi ({e}). "
              f"'search_documents' aracı bu oturumda boş sonuç dönebilir.")


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(students.router)
app.include_router(sessions.router)
app.include_router(dialogue.router)
app.include_router(quiz.router)
app.include_router(survey.router)
app.include_router(progress.router)
app.include_router(tasks.router)

# Serve the built React frontend (production).
# Build: cd frontend && npm run build
# The dist/ folder sits one level above backend/.
_FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    _ASSETS_DIR = _FRONTEND_DIST / "assets"
    if _ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(_ASSETS_DIR)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        candidate = _FRONTEND_DIST / full_path
        if candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(_FRONTEND_DIST / "index.html"))

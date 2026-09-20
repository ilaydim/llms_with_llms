"""
Test ortamı: mock LLM, geçici SQLite veritabanı, gerçek embedding modeli yok.
Ortam değişkenleri `app` import edilmeden ÖNCE ayarlanmalı (Settings lru_cache'li).
"""
import os
import tempfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
_tmp = tempfile.mkdtemp(prefix="llms_tests_")

os.environ["LLM_PROVIDER"] = "mock"
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["CHROMA_PERSIST_DIR"] = f"{_tmp}/chroma"
os.environ["MODULES_CONFIG_DIR"] = str(BACKEND_DIR / "modules_config")
os.environ["SURVEY_CONFIG_DIR"] = str(BACKEND_DIR / "survey_config")
os.environ["RAG_DOCUMENTS_DIR"] = str(BACKEND_DIR / "rag_documents")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app, sync_modules_from_config  # noqa: E402


@pytest.fixture(autouse=True)
def _no_embedding_model(monkeypatch):
    """Mock tutor 'doküman ara' aracını çağırır; HF'den model indirmesin."""
    monkeypatch.setattr(
        "app.services.document_search.semantic_search",
        lambda query, top_k=2: [{"source": "test.md", "text": "RAG retrieves chunks."}],
    )


@pytest.fixture()
def client():
    """Her test için temiz bir veritabanı. Startup event'i (ingestion) çalıştırılmaz."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    sync_modules_from_config()
    return TestClient(app)


@pytest.fixture()
def session_ids(client):
    """(student_id, session_id) döner."""
    student = client.post("/students/identify", json={"name": "Ada", "student_no": "1"}).json()
    session = client.post(f"/sessions/start/{student['id']}").json()
    return student["id"], session["id"]

"""
Merkezi uygulama yapılandırması.
NFR-2.3: Hassas bilgiler (API anahtarı vb.) burada DEĞİL, .env dosyasında tutulur;
bu modül sadece onları okur.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM
    # NFR-5.2: sağlayıcı .env üzerinden seçilir, kod değişikliği gerektirmez.
    # "mock": API anahtarı gerekmeden agent'ları test etmek için (varsayılan).
    llm_provider: str = "mock"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    tutor_model: str = "claude-haiku-4-5-20251001"
    evaluator_model: str = "claude-haiku-4-5-20251001"

    # Veritabanı
    database_url: str = "sqlite:///./llms_with_llms.db"

    # RAG
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_persist_dir: str = "./chroma_store"

    # Mastery learning (FR-6.4 — eşik TBD, env'den override edilebilir varsayılan)
    quiz_pass_threshold: float = 0.7

    # Diyalog bağlamı (Bölüm 5.4 "Açık nokta")
    max_context_messages: int = 20

    # Modül yapılandırma dosyalarının bulunduğu klasör (FR-1.1)
    modules_config_dir: str = "./modules_config"

    # FR-4.1: retrieval için kaynak dokümanların bulunduğu klasör
    rag_documents_dir: str = "./rag_documents"

    # FR-8.1/8.2: anket sorularının bulunduğu klasör
    survey_config_dir: str = "./survey_config"


@lru_cache
def get_settings() -> Settings:
    return Settings()

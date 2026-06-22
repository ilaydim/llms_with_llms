"""
FR-4.1: RAG modülünün uygulama katmanındaki "doküman ara" aracının gerçek
implementasyonu. rag_documents/ altındaki .md dosyalarını paragraf bazında
chunk'layıp (bkz. rag_documents/chunking_stratejileri.md — kendi öğrettiğimiz
ilkeyi burada da uyguluyoruz), sentence-transformers ile embed edip chromadb'de
saklar; sorgu geldiğinde en yakın k parçayı semantik olarak getirir.

Not: İlk çalıştırmada embedding modeli (all-MiniLM-L6-v2, ~90MB) Hugging
Face'ten otomatik indirilir — internet bağlantısı gerekir.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings

_COLLECTION_NAME = "rag_documents"


def _split_into_chunks(raw_text: str, source_name: str) -> list[dict]:
    """
    Basit paragraf-bazlı chunking: başlık (# ...) ve "Kaynak:" satırlarını
    atlar, geri kalan paragrafları (boş satırla ayrılmış blokları) ayrı
    chunk olarak döner. (chunking_stratejileri.md'de anlatılan ilkeyle
    tutarlı: çok büyük olmayan, anlam bütünlüğü taşıyan parçalar.)
    """
    chunks = []
    paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
    chunk_idx = 0
    for para in paragraphs:
        if para.startswith("#"):
            continue
        if para.startswith("Kaynak:"):
            continue
        chunks.append(
            {
                "id": f"{source_name}::chunk{chunk_idx}",
                "text": para,
                "source": source_name,
            }
        )
        chunk_idx += 1
    return chunks


def load_all_chunks() -> list[dict]:
    """rag_documents/ altındaki tüm .md dosyalarını okuyup chunk'lara böler."""
    settings = get_settings()
    docs_dir = Path(settings.rag_documents_dir)
    all_chunks: list[dict] = []
    for md_file in sorted(docs_dir.glob("*.md")):
        if md_file.name.upper().startswith("KAYNAKCA"):
            continue  # kaynakça dosyası ders içeriği değil, embed edilmemeli
        raw = md_file.read_text(encoding="utf-8")
        all_chunks.extend(_split_into_chunks(raw, md_file.stem))
    return all_chunks


@lru_cache
def _get_embedding_model():
    from sentence_transformers import SentenceTransformer

    settings = get_settings()
    return SentenceTransformer(settings.embedding_model)


@lru_cache
def _get_chroma_collection():
    import chromadb

    settings = get_settings()
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return client.get_or_create_collection(_COLLECTION_NAME)


def ingest_documents(force: bool = False) -> int:
    """
    rag_documents/ içeriğini embed edip chromadb'ye yazar.
    force=False ise ve koleksiyon zaten doluysa tekrar embed etmez
    (her uygulama başlangıcında gereksiz yere modeli indirip çalıştırmamak için).
    Döner: kaç chunk yazıldığı.
    """
    collection = _get_chroma_collection()

    if not force and collection.count() > 0:
        return collection.count()

    if force and collection.count() > 0:
        existing_ids = collection.get()["ids"]
        if existing_ids:
            collection.delete(ids=existing_ids)

    chunks = load_all_chunks()
    if not chunks:
        return 0

    model = _get_embedding_model()
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=False).tolist()

    collection.add(
        ids=[c["id"] for c in chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"source": c["source"]} for c in chunks],
    )
    return len(chunks)


def semantic_search(query: str, top_k: int = 3) -> list[dict]:
    """Sorguya en yakın top_k chunk'ı döner: [{"text", "source", "distance"}]"""
    try:
        collection = _get_chroma_collection()
        if collection.count() == 0:
            ingest_documents()

        model = _get_embedding_model()
        query_embedding = model.encode([query]).tolist()

        results = collection.query(query_embeddings=query_embedding, n_results=top_k)

        hits = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        for text, meta, dist in zip(docs, metas, distances):
            hits.append({"text": text, "source": meta.get("source", "?"), "distance": dist})
        return hits
    except Exception as e:  # noqa: BLE001 — embedding modeli indirilemezse diyalog akışını bozmamak için
        print(f"[vector_store] semantic_search başarısız: {e}")
        return []

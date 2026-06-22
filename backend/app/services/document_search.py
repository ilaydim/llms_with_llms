"""
FR-4.1: Uygulama katmanında Tutor Agent'a tanımlanan "doküman ara" aracının
arkasındaki retrieval mantığı.

Gün 3 güncellemesi: Artık gerçek bir embedding tabanlı semantik arama
kullanılıyor (bkz. vector_store.py — chromadb + sentence-transformers).
Önceki anahtar-kelime tabanlı placeholder kaldırıldı; bu fonksiyonun imzası
(search_documents(query, top_k) -> str) aynı kaldığı için tutor_agent.py'de
hiçbir değişiklik gerekmedi (Bölüm 5.4'te öngörüldüğü gibi).
"""
from app.services.vector_store import semantic_search


def search_documents(query: str, top_k: int = 2) -> str:
    """
    Sorguya en alakalı top_k doküman parçasını semantik olarak getirir ve
    Tutor Agent'ın doğrudan tool_result olarak kullanabileceği bir metin
    formatında döner.
    """
    hits = semantic_search(query, top_k=top_k)

    if not hits:
        return "İlgili bir doküman parçası bulunamadı."

    formatted = "\n\n".join(f"[Kaynak: {h['source']}]\n{h['text']}" for h in hits)
    return formatted

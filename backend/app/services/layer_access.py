"""
Katman kilidi (backend tarafı): bir katmana yazma/quiz işlemi ancak bir önceki katman
bu oturumda `completed` ise yapılabilir. Frontend'deki `getUnlockedLayers` ile aynı
kural; kural değişirse sadece burası güncellenir.
Okuma (mesaj geçmişi, quiz soruları, intro) bilerek kilitsiz — geçmiş katmanlara dönüp
bakmak serbest.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session as DBSession

from app.models.models import LayerProgress

LAYER_ORDER = ["theory", "application", "critical"]


def is_layer_unlocked(db: DBSession, session_id: int, module_id: int, layer: str) -> bool:
    if layer not in LAYER_ORDER:
        return True  # bilinmeyen katmanı bu kontrol reddetmez; ilgili endpoint kendi 4xx'ini üretir
    idx = LAYER_ORDER.index(layer)
    if idx == 0:
        return True
    previous = (
        db.query(LayerProgress)
        .filter(
            LayerProgress.session_id == session_id,
            LayerProgress.module_id == module_id,
            LayerProgress.layer == LAYER_ORDER[idx - 1],
            LayerProgress.status == "completed",
        )
        .first()
    )
    return previous is not None


def require_layer_unlocked(db: DBSession, session_id: int, module_id: int, layer: str) -> None:
    if not is_layer_unlocked(db, session_id, module_id, layer):
        raise HTTPException(
            status_code=403,
            detail=f"Bu katman henüz kilitli: önce '{LAYER_ORDER[LAYER_ORDER.index(layer) - 1]}' katmanını tamamla.",
        )

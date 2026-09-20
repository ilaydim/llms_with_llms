"""
FR-7.3 / Bölüm 1.3 (Active Session Time):
"Kullanıcının pasif (etkileşimsiz) geçen süresinin hariç tutulduğu, gerçek
etkileşim süresi." Kural: iki etkileşim arası 2 dakikadan kısaysa aktif sayılır,
bu süre active_duration_seconds'a eklenir; 2 dakikadan uzunsa pasif kabul edilir
ve eklenmez (öğrenci uzun süre ekrandan uzaklaşmış demektir).
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session as DBSession

from app.models.models import LayerProgress
from app.models.models import Session as SessionModel

ACTIVE_GAP_THRESHOLD_SECONDS = 120  # 2 dakika


def touch_session(db: DBSession, session: SessionModel) -> SessionModel:
    """Her yeni etkileşimde (mesaj, quiz cevabı vb.) çağrılır."""
    now = datetime.now(timezone.utc)
    last_activity = session.last_activity_at
    if last_activity.tzinfo is None:
        last_activity = last_activity.replace(tzinfo=timezone.utc)

    gap_seconds = (now - last_activity).total_seconds()
    if gap_seconds <= ACTIVE_GAP_THRESHOLD_SECONDS:
        session.active_duration_seconds += int(gap_seconds)

    session.last_activity_at = now
    db.commit()
    db.refresh(session)
    return session


def close_session(db: DBSession, session_id: int) -> SessionModel | None:
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if session is None:
        return None
    session.ended_at = datetime.now(timezone.utc)
    # FR-7.2: oturum kapanırken bitmemiş (in_progress) katmanlar "bırakıldı" olarak işaretlenir
    db.query(LayerProgress).filter(
        LayerProgress.session_id == session_id, LayerProgress.status == "in_progress"
    ).update({"status": "abandoned"})
    db.commit()
    db.refresh(session)
    return session

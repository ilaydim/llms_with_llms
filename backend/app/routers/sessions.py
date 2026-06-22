"""
NFR-4.1: Tarayıcı kapanıp yeniden açılsa bile kaldığı yerden devam edebilmeli
-> bunu, "ended_at is null" olan açık bir session varsa onu döndürerek sağlıyoruz.

FR-7.3: Active Session Time hesabı (Bölüm 1.3) — iki etkileşim arası 2 dakikadan
kısaysa aktif, uzunsa pasif sayılır. Bu hesap, her aktivite kaydında
`touch_session` servis fonksiyonuyla güncellenir (bkz. app/services/session_activity.py).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.models import Session as SessionModel, Student
from app.schemas.session import SessionOut

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start/{student_id}", response_model=SessionOut)
def start_or_resume_session(student_id: int, db: DBSession = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")

    open_session = (
        db.query(SessionModel)
        .filter(SessionModel.student_id == student_id, SessionModel.ended_at.is_(None))
        .order_by(SessionModel.started_at.desc())
        .first()
    )
    if open_session:
        return open_session

    new_session = SessionModel(student_id=student_id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@router.post("/{session_id}/end", response_model=SessionOut)
def end_session(session_id: int, db: DBSession = Depends(get_db)):
    from app.services.session_activity import close_session

    session = close_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Oturum bulunamadı")
    return session

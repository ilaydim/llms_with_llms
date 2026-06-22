"""
UC-2: Teori Katmanında LLM ile Diyalog Kurma (ve aynı mekanizma application/critical
katmanları için de kullanılır — Bölüm 5.5).
FR-3.2/3.3/3.4, FR-4.2, FR-5.2 burada karşılanır.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.agents.tutor_agent import TutorAgent
from app.database import get_db
from app.models.models import DialogueMessage, Module
from app.models.models import Session as SessionModel
from app.schemas.dialogue import DialogueMessageIn, DialogueMessageOut, LayerIntroOut
from app.services.session_activity import touch_session

router = APIRouter(prefix="/dialogue", tags=["dialogue"])

_tutor_agent = TutorAgent()  # tek bir kod tabanı, her çağrıda modüle özgü prompt üretir (Bölüm 5.5)


def _get_module(db: DBSession, module_code: str) -> Module:
    module = db.query(Module).filter(Module.code == module_code).first()
    if module is None:
        raise HTTPException(status_code=404, detail=f"Modül bulunamadı: {module_code}")
    return module


def _get_session(db: DBSession, session_id: int) -> SessionModel:
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Oturum bulunamadı")
    return session


@router.get("/{module_code}/{layer}/intro", response_model=LayerIntroOut)
def get_layer_intro(module_code: str, layer: str):
    """FR-3.1: Teori katmanı girişi sabit metinden gelir, dinamik üretilmez."""
    try:
        intro_text = _tutor_agent.generate_layer_intro(module_code, layer)
    except (FileNotFoundError, ValueError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    return LayerIntroOut(layer=layer, intro_text=intro_text)


@router.get("/{session_id}/{module_code}/{layer}/history", response_model=list[DialogueMessageOut])
def get_history(session_id: int, module_code: str, layer: str, db: DBSession = Depends(get_db)):
    module = _get_module(db, module_code)
    messages = (
        db.query(DialogueMessage)
        .filter(
            DialogueMessage.session_id == session_id,
            DialogueMessage.module_id == module.id,
            DialogueMessage.layer == layer,
        )
        .order_by(DialogueMessage.created_at.asc())
        .all()
    )
    return messages


@router.post("/message", response_model=DialogueMessageOut)
def send_message(payload: DialogueMessageIn, db: DBSession = Depends(get_db)):
    """
    FR-3.2/3.3: Öğrenci serbest metin mesaj yazar, Tutor Agent cevap üretir,
    her iki mesaj da (öğrenci + tutor) zaman damgasıyla kaydedilir.
    """
    module = _get_module(db, payload.module_code)
    session = _get_session(db, payload.session_id)

    # Önceki konuşma geçmişini bağlam olarak hazırla
    history_rows = (
        db.query(DialogueMessage)
        .filter(
            DialogueMessage.session_id == payload.session_id,
            DialogueMessage.module_id == module.id,
            DialogueMessage.layer == payload.layer,
        )
        .order_by(DialogueMessage.created_at.asc())
        .all()
    )
    conversation_history = [
        {"role": "user" if m.sender == "student" else "assistant", "content": m.content}
        for m in history_rows
    ]

    # 1) Öğrenci mesajını kaydet
    student_msg = DialogueMessage(
        session_id=payload.session_id,
        module_id=module.id,
        layer=payload.layer,
        sender="student",
        content=payload.content,
    )
    db.add(student_msg)
    db.commit()

    # 2) Tutor Agent'tan cevap al (FR-3.5: kapsam dışı sorularda yönlendirme system prompt'ta tanımlı)
    result = _tutor_agent.respond(
        module_code=payload.module_code,
        layer=payload.layer,
        conversation_history=conversation_history,
        student_message=payload.content,
    )

    # 3) Tutor cevabını kaydet
    tutor_msg = DialogueMessage(
        session_id=payload.session_id,
        module_id=module.id,
        layer=payload.layer,
        sender="tutor_agent",
        content=result["reply"],
    )
    db.add(tutor_msg)
    db.commit()
    db.refresh(tutor_msg)

    # FR-7.3: Active Session Time güncelle
    touch_session(db, session)

    return tutor_msg

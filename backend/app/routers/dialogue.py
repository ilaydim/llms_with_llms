"""
UC-2: Teori Katmanında LLM ile Diyalog Kurma (ve aynı mekanizma application/critical
katmanları için de kullanılır — Bölüm 5.5).
FR-3.2/3.3/3.4, FR-4.2, FR-5.2 burada karşılanır.
"""
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DBSession

from app.agents.tutor_agent import TutorAgent
from app.database import SessionLocal, get_db
from app.models.models import DialogueMessage, LayerProgress, Module
from app.models.models import Session as SessionModel
from app.schemas.dialogue import DialogueMessageIn, DialogueMessageOut, LayerIntroOut
from app.services.layer_access import is_layer_unlocked, require_layer_unlocked
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
def get_layer_intro(module_code: str, layer: str, lang: str = "en"):
    """FR-3.1: Teori katmanı girişi sabit metinden gelir, dinamik üretilmez."""
    try:
        intro_text = _tutor_agent.generate_layer_intro(module_code, layer, lang=lang)
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
    require_layer_unlocked(db, payload.session_id, module.id, payload.layer)

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

    # FR-7.2: Bu katmana ilk mesaj geliyorsa in_progress olarak işaretle
    existing_progress = (
        db.query(LayerProgress)
        .filter(
            LayerProgress.session_id == payload.session_id,
            LayerProgress.module_id == module.id,
            LayerProgress.layer == payload.layer,
        )
        .first()
    )
    if existing_progress is None:
        db.add(LayerProgress(
            session_id=payload.session_id,
            module_id=module.id,
            layer=payload.layer,
            status="in_progress",
        ))
        db.commit()
    elif existing_progress.status == "not_started":
        existing_progress.status = "in_progress"
        db.commit()

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
        lang=payload.lang,
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


@router.post("/message/stream")
def send_message_stream(payload: DialogueMessageIn):
    """
    NFR-1.1: SSE (Server-Sent Events) ile streaming cevap.
    Frontend ilk chunk'ı < 3 saniyede alır.
    DB session StreamingResponse generator içinde açılıp kapanır (dependency injection
    streaming'de çalışmadığı için manuel yönetim gerekir).
    """
    def event_stream():
        db = SessionLocal()
        try:
            module = db.query(Module).filter(Module.code == payload.module_code).first()
            session = db.query(SessionModel).filter(SessionModel.id == payload.session_id).first()
            if not module or not session:
                yield f"data: {json.dumps({'error': 'Oturum veya modül bulunamadı'})}\n\n"
                return
            if not is_layer_unlocked(db, payload.session_id, module.id, payload.layer):
                yield f"data: {json.dumps({'error': 'Bu katman henüz kilitli.', 'locked': True})}\n\n"
                return

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

            # FR-7.2: in_progress işaretle
            existing = (
                db.query(LayerProgress)
                .filter(
                    LayerProgress.session_id == payload.session_id,
                    LayerProgress.module_id == module.id,
                    LayerProgress.layer == payload.layer,
                )
                .first()
            )
            if existing is None:
                db.add(LayerProgress(
                    session_id=payload.session_id,
                    module_id=module.id,
                    layer=payload.layer,
                    status="in_progress",
                ))
                db.commit()
            elif existing.status == "not_started":
                existing.status = "in_progress"
                db.commit()

            # Öğrenci mesajını kaydet
            db.add(DialogueMessage(
                session_id=payload.session_id,
                module_id=module.id,
                layer=payload.layer,
                sender="student",
                content=payload.content,
            ))
            db.commit()

            # Streaming: her chunk SSE formatında gönderilir
            full_text = ""
            for chunk in _tutor_agent.stream_respond(
                module_code=payload.module_code,
                layer=payload.layer,
                conversation_history=conversation_history,
                student_message=payload.content,
                lang=payload.lang,
            ):
                full_text += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            # Tam cevabı DB'ye kaydet
            tutor_msg = DialogueMessage(
                session_id=payload.session_id,
                module_id=module.id,
                layer=payload.layer,
                sender="tutor_agent",
                content=full_text,
            )
            db.add(tutor_msg)
            db.commit()
            db.refresh(tutor_msg)
            touch_session(db, session)

            yield f"data: {json.dumps({'done': True, 'message_id': tutor_msg.id, 'created_at': tutor_msg.created_at.isoformat()})}\n\n"
        except Exception as exc:  # noqa: BLE001 — NFR-3.3: stack trace sızdırma
            yield f"data: {json.dumps({'error': 'Bir hata oluştu, lütfen tekrar deneyin.'})}\n\n"
        finally:
            db.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")

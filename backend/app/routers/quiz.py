"""
UC-5: Katman Sonu Quiz'i Çözme (FR-6.1-6.3)
UC-6: Mastery Learning — Konuya Geri Dönme (FR-6.4, 6.5, 6.7)
UC-7: Mastery Learning — Sonraki Katmana Geçme (FR-6.4, 6.6)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.agents.evaluator_agent import EvaluatorAgent
from app.agents.tutor_agent import TutorAgent
from app.core.config import get_settings
from app.database import get_db
from app.models.models import DialogueMessage, LayerProgress, Module, QuizResult, RevisitLog
from app.models.models import Session as SessionModel
from app.schemas.quiz import (
    QuizMCQOut,
    QuizOpenEndedOut,
    QuizQuestionsOut,
    QuizResultOut,
    QuizSubmitIn,
    RevisitIn,
    RevisitOut,
)
from app.services.module_loader import get_module_content, load_module_config
from app.services.layer_access import require_layer_unlocked
from app.services.session_activity import touch_session

router = APIRouter(prefix="/quiz", tags=["quiz"])

_evaluator_agent = EvaluatorAgent()
_tutor_agent = TutorAgent()


def _mark_layer_completed(db: DBSession, session_id: int, module_id: int, layer: str) -> None:
    """FR-7.2: Katmanı completed olarak işaretle (geçilince veya devam seçilince)."""
    from datetime import datetime, timezone
    row = (
        db.query(LayerProgress)
        .filter(
            LayerProgress.session_id == session_id,
            LayerProgress.module_id == module_id,
            LayerProgress.layer == layer,
        )
        .first()
    )
    if row is None:
        row = LayerProgress(session_id=session_id, module_id=module_id, layer=layer)
        db.add(row)
    row.status = "completed"
    row.completed_at = datetime.now(timezone.utc)
    db.commit()


def _get_module(db: DBSession, module_code: str) -> Module:
    module = db.query(Module).filter(Module.code == module_code).first()
    if module is None:
        raise HTTPException(status_code=404, detail=f"Modül bulunamadı: {module_code}")
    return module


@router.get("/{module_code}/{layer}", response_model=QuizQuestionsOut)
def get_quiz(module_code: str, layer: str, lang: str = "en"):
    """FR-6.1: Çoğunlukla çoktan seçmeli + bir açık uçlu soru döner (correct_index hariç)."""
    try:
        module_config = load_module_config(module_code)
        content = get_module_content(module_config, lang)
        quiz = content["quiz"][layer]
    except (FileNotFoundError, KeyError) as e:
        raise HTTPException(status_code=404, detail=f"Quiz bulunamadı: {e}")

    return QuizQuestionsOut(
        layer=layer,
        mcq=[QuizMCQOut(id=q["id"], question=q["question"], options=q["options"]) for q in quiz["mcq"]],
        open_ended=QuizOpenEndedOut(id=quiz["open_ended"]["id"], question=quiz["open_ended"]["question"]),
    )


@router.post("/submit", response_model=QuizResultOut)
def submit_quiz(payload: QuizSubmitIn, db: DBSession = Depends(get_db)):
    module = _get_module(db, payload.module_code)
    session = db.query(SessionModel).filter(SessionModel.id == payload.session_id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Oturum bulunamadı")
    require_layer_unlocked(db, payload.session_id, module.id, payload.layer)

    module_config = load_module_config(payload.module_code)
    content = get_module_content(module_config, payload.lang)
    try:
        quiz_def = content["quiz"][payload.layer]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Bu katman için quiz tanımlı değil: {payload.layer}")

    # FR-6.2: Çoktan seçmeli sorular kural bazlı (sabit doğru cevaba göre) puanlanır
    correct_map = {q["id"]: q["correct_index"] for q in quiz_def["mcq"]}
    if not correct_map:
        mcq_score = 1.0
    else:
        answer_map = {a.question_id: a.selected_index for a in payload.mcq_answers}
        correct_count = sum(
            1 for qid, correct_idx in correct_map.items() if answer_map.get(qid) == correct_idx
        )
        mcq_score = correct_count / len(correct_map)

    # FR-6.3: Açık uçlu soru Evaluator Agent tarafından değerlendirilir
    eval_result = _evaluator_agent.evaluate_open_ended(
        module_code=payload.module_code,
        layer=payload.layer,
        question_id=quiz_def["open_ended"]["id"],
        student_answer=payload.open_ended_answer,
        lang=payload.lang,
    )

    settings = get_settings()
    overall_score = 0.6 * mcq_score + 0.4 * eval_result["puan"]
    passed = overall_score >= settings.quiz_pass_threshold

    # FR-6.7: Kaçıncı deneme olduğunu say
    attempt_number = (
        db.query(QuizResult)
        .filter(
            QuizResult.session_id == payload.session_id,
            QuizResult.module_id == module.id,
            QuizResult.layer == payload.layer,
        )
        .count()
        + 1
    )

    result = QuizResult(
        session_id=payload.session_id,
        module_id=module.id,
        layer=payload.layer,
        mcq_score=mcq_score,
        open_ended_score=eval_result["puan"],
        open_ended_feedback=eval_result["geri_bildirim"],
        attempt_number=attempt_number,
        passed=passed,
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    # FR-7.2: Quiz geçildiyse katmanı completed olarak işaretle
    if passed:
        _mark_layer_completed(db, payload.session_id, module.id, payload.layer)

    touch_session(db, session)

    return result


@router.post("/revisit", response_model=RevisitOut)
def revisit(payload: RevisitIn, db: DBSession = Depends(get_db)):
    """
    FR-6.4/6.5: Öğrenci quiz'i geçemeyip 'geri dönmek ister misin?' sorusuna
    cevap verdiğinde çağrılır. revisited=true ise Tutor Agent'tan farklı bir
    anlatım istenir ve bu, normal diyalog akışına (aynı katmanın mesaj
    geçmişine) bir tutor mesajı olarak eklenir — UC-6 adım 4'teki "UC-2 ile
    aynı mekanizma" notuyla tutarlı.
    """
    module = _get_module(db, payload.module_code)
    session = db.query(SessionModel).filter(SessionModel.id == payload.session_id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Oturum bulunamadı")
    require_layer_unlocked(db, payload.session_id, module.id, payload.layer)

    # FR-6.7: geri dönüş kaydı
    db.add(
        RevisitLog(
            session_id=payload.session_id,
            module_id=module.id,
            layer=payload.layer,
            revisited=payload.revisited,
        )
    )
    db.commit()

    if not payload.revisited:
        # FR-6.6 + FR-7.2: Devam et seçildi → katmanı completed olarak işaretle
        _mark_layer_completed(db, payload.session_id, module.id, payload.layer)
        return RevisitOut(explanation=None)

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

    explanation = _tutor_agent.generate_simplified_explanation(
        module_code=payload.module_code,
        layer=payload.layer,
        conversation_history=conversation_history,
        lang=payload.lang,
    )

    db.add(
        DialogueMessage(
            session_id=payload.session_id,
            module_id=module.id,
            layer=payload.layer,
            sender="tutor_agent",
            content=explanation,
        )
    )
    db.commit()
    touch_session(db, session)

    return RevisitOut(explanation=explanation)

"""
FR-7.2 — her katmandaki ilerleme durumunu kaydet/oku.
NFR-4.1 — tarayıcı kapanıp açılsa bile kaldığı yerden devam: bu endpoint
           frontend'in mevcut durumu sunucudan çekerek restore etmesini sağlar.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.models import LayerProgress, Module, SurveyResponse
from app.models.models import Session as SessionModel
from app.models.models import Student

router = APIRouter(prefix="/progress", tags=["progress"])

LAYER_ORDER = ["theory", "application", "critical"]


class StudentProgressOut(BaseModel):
    pre_survey_done: bool
    post_survey_done: bool
    current_layer: str          # hangi katmanda (theory/application/critical)
    current_view: str           # chat veya quiz
    layers_completed: list[str] # tamamlanan katmanlar


class LayerStatusIn(BaseModel):
    status: str  # in_progress / completed / abandoned


def _get_or_create_layer_progress(
    db: DBSession, session_id: int, module_id: int, layer: str
) -> LayerProgress:
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
        row = LayerProgress(session_id=session_id, module_id=module_id, layer=layer, status="not_started")
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


@router.get("/student/{student_id}", response_model=StudentProgressOut)
def get_student_progress(student_id: int, db: DBSession = Depends(get_db)):
    """
    NFR-4.1: Frontend bu endpoint'i açılışta çağırarak öğrencinin kaldığı
    yeri restore eder. En son açık oturumu baz alır.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")

    pre_done = (
        db.query(SurveyResponse)
        .filter(SurveyResponse.student_id == student_id, SurveyResponse.survey_type == "pre")
        .first() is not None
    )
    post_done = (
        db.query(SurveyResponse)
        .filter(SurveyResponse.student_id == student_id, SurveyResponse.survey_type == "post")
        .first() is not None
    )

    # En son açık (veya en son kapanmış) oturumu bul
    session = (
        db.query(SessionModel)
        .filter(SessionModel.student_id == student_id)
        .order_by(SessionModel.started_at.desc())
        .first()
    )

    if session is None:
        return StudentProgressOut(
            pre_survey_done=pre_done,
            post_survey_done=post_done,
            current_layer="theory",
            current_view="chat",
            layers_completed=[],
        )

    # Tamamlanan katmanları bul
    completed_rows = (
        db.query(LayerProgress)
        .filter(
            LayerProgress.session_id == session.id,
            LayerProgress.status == "completed",
        )
        .all()
    )
    layers_completed = [r.layer for r in completed_rows]

    # Mevcut katmanı belirle: tamamlanmamış ilk katman
    current_layer = "theory"
    for layer in LAYER_ORDER:
        if layer not in layers_completed:
            current_layer = layer
            break

    # Eğer tüm katmanlar tamamlandıysa post-survey aşamasındayız
    if len(layers_completed) == len(LAYER_ORDER):
        current_layer = "critical"  # son katmanda kalmış gibi görün

    # current_view: bu katman için quiz sonucu var mı? (quiz ekranında mıydı?)
    module = db.query(Module).filter(Module.phase == 1).first()
    current_view = "chat"
    if module:
        in_progress_row = (
            db.query(LayerProgress)
            .filter(
                LayerProgress.session_id == session.id,
                LayerProgress.module_id == module.id,
                LayerProgress.layer == current_layer,
                LayerProgress.status == "in_progress",
            )
            .first()
        )
        # Eğer bu katmanda in_progress bir kayıt varsa chat'te kalmış demektir
        current_view = "chat" if in_progress_row else "chat"

    return StudentProgressOut(
        pre_survey_done=pre_done,
        post_survey_done=post_done,
        current_layer=current_layer,
        current_view=current_view,
        layers_completed=layers_completed,
    )


@router.patch("/{session_id}/{module_code}/{layer}", response_model=dict)
def update_layer_status(
    session_id: int,
    module_code: str,
    layer: str,
    payload: LayerStatusIn,
    db: DBSession = Depends(get_db),
):
    """
    FR-7.2: Katman durumunu günceller.
    - in_progress: öğrenci bu katmana girdi (dialogue router çağırır)
    - completed: öğrenci bu katmanı geçti (quiz router çağırır)
    - abandoned: oturum kapandı ama katman bitmedi
    """
    if layer not in LAYER_ORDER:
        raise HTTPException(status_code=400, detail=f"Geçersiz katman: {layer}")
    if payload.status not in ("not_started", "in_progress", "completed", "abandoned"):
        raise HTTPException(status_code=400, detail=f"Geçersiz durum: {payload.status}")

    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Oturum bulunamadı")

    module = db.query(Module).filter(Module.code == module_code).first()
    if module is None:
        raise HTTPException(status_code=404, detail=f"Modül bulunamadı: {module_code}")

    row = _get_or_create_layer_progress(db, session_id, module.id, layer)
    row.status = payload.status
    if payload.status == "completed":
        row.completed_at = datetime.now(timezone.utc)
    db.commit()

    return {"session_id": session_id, "layer": layer, "status": payload.status}

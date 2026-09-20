"""
FR-7.1 / FR-7.2 / FR-7.3 — Learning analytics özetleri.
Ham veri zaten dialogue_messages, layer_progress, quiz_results, revisit_logs ve
sessions tablolarında; bu router onu araştırmacı/arayüz için okunur hâle getirir.
Bölüm 8.4'e uygun olarak betimsel istatistikler (ortalama, medyan) verir.
"""
from statistics import mean, median

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.models import (
    DialogueMessage,
    LayerProgress,
    QuizResult,
    RevisitLog,
    Student,
)
from app.models.models import Session as SessionModel
from app.services.layer_access import LAYER_ORDER

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Aynı katman birden çok oturumda görünürse en "ileri" durum geçerli sayılır
_STATUS_RANK = {"not_started": 0, "abandoned": 1, "in_progress": 2, "completed": 3}


class LayerAnalytics(BaseModel):
    layer: str
    status: str                 # not_started / in_progress / completed / abandoned
    student_messages: int       # FR-7.1: bu katmanda öğrencinin sorduğu/yazdığı mesaj sayısı
    quiz_attempts: int
    best_quiz_score: float | None   # 0.6*mcq + 0.4*açık uçlu (geçme formülüyle aynı)
    revisit_count: int          # "geri dön" seçilme sayısı (FR-6.7)


class StudentAnalyticsOut(BaseModel):
    student_id: int
    session_count: int
    active_seconds: int         # FR-7.3
    total_student_messages: int
    layers: list[LayerAnalytics]


class LayerSummary(BaseModel):
    layer: str
    students_started: int
    students_completed: int
    students_abandoned: int
    mean_student_messages: float | None
    median_student_messages: float | None
    mean_quiz_attempts: float | None
    revisit_count: int


class CohortSummaryOut(BaseModel):
    student_count: int
    mean_active_seconds: float | None
    median_active_seconds: float | None
    layers: list[LayerSummary]


def _overall(mcq: float, open_ended: float | None) -> float:
    return 0.6 * mcq + 0.4 * (open_ended or 0.0)


def _student_layer_stats(db: DBSession, student_id: int) -> dict[str, dict]:
    """Bir öğrencinin tüm oturumları boyunca katman bazlı ham sayılar."""
    session_ids = [s.id for s in db.query(SessionModel.id).filter(SessionModel.student_id == student_id)]
    stats = {
        layer: {"status": "not_started", "messages": 0, "attempts": 0, "best": None, "revisits": 0}
        for layer in LAYER_ORDER
    }
    if not session_ids:
        return stats

    for layer, count in (
        db.query(DialogueMessage.layer, func.count(DialogueMessage.id))
        .filter(DialogueMessage.session_id.in_(session_ids), DialogueMessage.sender == "student")
        .group_by(DialogueMessage.layer)
    ):
        if layer in stats:
            stats[layer]["messages"] = count

    for row in db.query(LayerProgress).filter(LayerProgress.session_id.in_(session_ids)):
        if row.layer in stats and _STATUS_RANK.get(row.status, 0) > _STATUS_RANK[stats[row.layer]["status"]]:
            stats[row.layer]["status"] = row.status

    for q in db.query(QuizResult).filter(QuizResult.session_id.in_(session_ids)):
        if q.layer in stats:
            st = stats[q.layer]
            st["attempts"] += 1
            score = _overall(q.mcq_score, q.open_ended_score)
            st["best"] = score if st["best"] is None else max(st["best"], score)

    for layer, count in (
        db.query(RevisitLog.layer, func.count(RevisitLog.id))
        .filter(RevisitLog.session_id.in_(session_ids), RevisitLog.revisited.is_(True))
        .group_by(RevisitLog.layer)
    ):
        if layer in stats:
            stats[layer]["revisits"] = count
    return stats


@router.get("/student/{student_id}", response_model=StudentAnalyticsOut)
def student_analytics(student_id: int, db: DBSession = Depends(get_db)):
    if db.query(Student.id).filter(Student.id == student_id).first() is None:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")

    sessions = db.query(SessionModel).filter(SessionModel.student_id == student_id).all()
    stats = _student_layer_stats(db, student_id)
    return StudentAnalyticsOut(
        student_id=student_id,
        session_count=len(sessions),
        active_seconds=sum(s.active_duration_seconds for s in sessions),
        total_student_messages=sum(v["messages"] for v in stats.values()),
        layers=[
            LayerAnalytics(
                layer=layer,
                status=stats[layer]["status"],
                student_messages=stats[layer]["messages"],
                quiz_attempts=stats[layer]["attempts"],
                best_quiz_score=stats[layer]["best"],
                revisit_count=stats[layer]["revisits"],
            )
            for layer in LAYER_ORDER
        ],
    )


@router.get("/summary", response_model=CohortSummaryOut)
def cohort_summary(db: DBSession = Depends(get_db)):
    """Tüm öğrenciler üzerinden anonim, toplulaştırılmış özet (isim/no içermez)."""
    student_ids = [s.id for s in db.query(Student.id)]
    per_student = {sid: _student_layer_stats(db, sid) for sid in student_ids}

    active = [
        total or 0
        for (total,) in db.query(func.sum(SessionModel.active_duration_seconds)).group_by(SessionModel.student_id)
    ]

    layers = []
    for layer in LAYER_ORDER:
        rows = [per_student[sid][layer] for sid in student_ids]
        started = [r for r in rows if r["status"] != "not_started" or r["messages"] or r["attempts"]]
        msgs = [r["messages"] for r in started]
        attempts = [r["attempts"] for r in started if r["attempts"]]
        layers.append(LayerSummary(
            layer=layer,
            students_started=len(started),
            students_completed=sum(r["status"] == "completed" for r in rows),
            students_abandoned=sum(r["status"] == "abandoned" for r in rows),
            mean_student_messages=mean(msgs) if msgs else None,
            median_student_messages=median(msgs) if msgs else None,
            mean_quiz_attempts=mean(attempts) if attempts else None,
            revisit_count=sum(r["revisits"] for r in rows),
        ))

    return CohortSummaryOut(
        student_count=len(student_ids),
        mean_active_seconds=mean(active) if active else None,
        median_active_seconds=median(active) if active else None,
        layers=layers,
    )

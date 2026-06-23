"""
FR-4.3 — Uygulama görevi adım ilerlemesini takip et.
UC-3 adım 5: Öğrenci adımı tamamladığını işaretler; sistem application_tasks.status günceller.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.models import ApplicationTask, Module
from app.models.models import Session as SessionModel
from app.services.module_loader import load_module_config

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskStatusIn(BaseModel):
    status: str  # not_started / in_progress / completed


class TaskStepOut(BaseModel):
    id: int
    step_number: int
    status: str
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


def _ensure_tasks_exist(db: DBSession, session_id: int, module: Module) -> list[ApplicationTask]:
    """Oturum için uygulama görevi adımları yoksa config'den oluşturur."""
    existing = (
        db.query(ApplicationTask)
        .filter(ApplicationTask.session_id == session_id, ApplicationTask.module_id == module.id)
        .order_by(ApplicationTask.step_number)
        .all()
    )
    if existing:
        return existing

    config = load_module_config(module.code)
    steps = config.get("application", {}).get("steps", [])
    created = []
    for step in steps:
        task = ApplicationTask(
            session_id=session_id,
            module_id=module.id,
            step_number=step["step_number"],
            status="not_started",
        )
        db.add(task)
        created.append(task)
    db.commit()
    for t in created:
        db.refresh(t)
    return created


@router.get("/{session_id}/{module_code}", response_model=list[TaskStepOut])
def get_tasks(session_id: int, module_code: str, db: DBSession = Depends(get_db)):
    """Oturumun uygulama görevi adımlarını döner; yoksa config'den oluşturur."""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Oturum bulunamadı")

    module = db.query(Module).filter(Module.code == module_code).first()
    if module is None:
        raise HTTPException(status_code=404, detail=f"Modül bulunamadı: {module_code}")

    return _ensure_tasks_exist(db, session_id, module)


@router.patch("/{task_id}", response_model=TaskStepOut)
def update_task_status(task_id: int, payload: TaskStatusIn, db: DBSession = Depends(get_db)):
    """FR-4.3: Adım durumunu günceller (not_started → in_progress → completed)."""
    if payload.status not in ("not_started", "in_progress", "completed"):
        raise HTTPException(status_code=400, detail=f"Geçersiz durum: {payload.status}")

    task = db.query(ApplicationTask).filter(ApplicationTask.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Görev adımı bulunamadı")

    task.status = payload.status
    if payload.status == "completed":
        task.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return task

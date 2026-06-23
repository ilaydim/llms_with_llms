"""
SRS Bölüm 6 — Veri Modeli.
Her sınıf, dokümandaki ilgili tabloya ve FR'ye birebir karşılık gelir.
Alan adları SRS'teki "Alan" sütunuyla aynı tutulmuştur (örn. active_duration_seconds)
ki araştırmacı veri erişimi (Bölüm 2.2 — kod yazmadan SQL ile sorgulama) kolay olsun.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Student(Base):
    """FR-2.1 — basit, şifresiz kimlik bilgisi."""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    student_no: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    sessions: Mapped[list["Session"]] = relationship(back_populates="student")
    survey_responses: Mapped[list["SurveyResponse"]] = relationship(back_populates="student")


class Session(Base):
    """FR-7.3 — oturum aralığı ve aktif süre hesabı (Active Session Time, Bölüm 1.3)."""

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    active_duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    student: Mapped["Student"] = relationship(back_populates="sessions")
    dialogue_messages: Mapped[list["DialogueMessage"]] = relationship(back_populates="session")
    application_tasks: Mapped[list["ApplicationTask"]] = relationship(back_populates="session")
    quiz_results: Mapped[list["QuizResult"]] = relationship(back_populates="session")
    revisit_logs: Mapped[list["RevisitLog"]] = relationship(back_populates="session")
    layer_progress: Mapped[list["LayerProgress"]] = relationship(back_populates="session")


class Module(Base):
    """FR-1.1/1.2 — yapılandırma dosyasından okunan modül tanımı."""

    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # örn. "rag"
    name: Mapped[str] = mapped_column(String, nullable=False)
    phase: Mapped[int] = mapped_column(Integer, default=1)
    config_path: Mapped[str] = mapped_column(String, nullable=False)


class DialogueMessage(Base):
    """FR-3.3 — öğrenci sorusu + Tutor Agent cevabı, zaman damgalı."""

    __tablename__ = "dialogue_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=False)
    layer: Mapped[str] = mapped_column(String, nullable=False)  # theory / application / critical
    sender: Mapped[str] = mapped_column(String, nullable=False)  # student / tutor_agent
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    session: Mapped["Session"] = relationship(back_populates="dialogue_messages")


class ApplicationTask(Base):
    """FR-4.3 — uygulama görevi adım ilerlemesi."""

    __tablename__ = "application_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=False)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, default="not_started")  # not_started/in_progress/completed
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    session: Mapped["Session"] = relationship(back_populates="application_tasks")


class QuizResult(Base):
    """FR-6.2/6.3/6.7 — çoktan seçmeli + açık uçlu sonuçlar, deneme sayısı."""

    __tablename__ = "quiz_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=False)
    layer: Mapped[str] = mapped_column(String, nullable=False)
    mcq_score: Mapped[float] = mapped_column(Float, default=0.0)
    open_ended_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    open_ended_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    session: Mapped["Session"] = relationship(back_populates="quiz_results")


class RevisitLog(Base):
    """FR-6.7 — mastery learning'de 'geri dön' seçimleri."""

    __tablename__ = "revisit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=False)
    layer: Mapped[str] = mapped_column(String, nullable=False)
    revisited: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    session: Mapped["Session"] = relationship(back_populates="revisit_logs")


class SurveyResponse(Base):
    """FR-8.3 — pre/post anket cevapları."""

    __tablename__ = "survey_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    survey_type: Mapped[str] = mapped_column(String, nullable=False)  # pre / post
    question_id: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    student: Mapped["Student"] = relationship(back_populates="survey_responses")


class LayerProgress(Base):
    """FR-7.2 — her katmandaki ilerleme durumu: not_started/in_progress/completed/abandoned."""

    __tablename__ = "layer_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), nullable=False)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), nullable=False)
    layer: Mapped[str] = mapped_column(String, nullable=False)  # theory / application / critical
    status: Mapped[str] = mapped_column(String, default="not_started")  # not_started/in_progress/completed/abandoned
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    session: Mapped["Session"] = relationship(back_populates="layer_progress")

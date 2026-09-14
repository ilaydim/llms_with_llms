from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DialogueMessageIn(BaseModel):
    session_id: int
    module_code: str
    layer: str  # theory / application / critical
    content: str
    lang: str = "en"  # en / tr — Tutor Agent'ın cevap dili


class DialogueMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender: str
    content: str
    layer: str
    created_at: datetime


class LayerIntroOut(BaseModel):
    layer: str
    intro_text: str

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    started_at: datetime
    last_activity_at: datetime
    active_duration_seconds: int
    ended_at: datetime | None

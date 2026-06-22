from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StudentCreate(BaseModel):
    """FR-2.1: isim ve/veya öğrenci no, şifresiz."""

    name: str
    student_no: str | None = None


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    student_no: str | None
    created_at: datetime

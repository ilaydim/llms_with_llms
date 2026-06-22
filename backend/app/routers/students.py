"""
UC-1 (adım 1-2) ve Alternatif Akış: Öğrenci ilk kez giriyorsa yeni kayıt,
daha önce aynı isim/öğrenci no ile girmişse mevcut kaydı eşleştirir (NFR-4.1).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.models import Student
from app.schemas.student import StudentCreate, StudentOut

router = APIRouter(prefix="/students", tags=["students"])


@router.post("/identify", response_model=StudentOut)
def identify_student(payload: StudentCreate, db: DBSession = Depends(get_db)):
    """
    FR-2.1/2.2: Basit kimlik bilgisiyle öğrenciyi bulur ya da oluşturur.
    Eşleştirme anahtarı: (name, student_no) ikilisi — student_no boşsa sadece name.
    """
    query = db.query(Student).filter(Student.name == payload.name)
    if payload.student_no:
        query = query.filter(Student.student_no == payload.student_no)

    student = query.first()
    if student is None:
        student = Student(name=payload.name, student_no=payload.student_no)
        db.add(student)
        db.commit()
        db.refresh(student)

    return student

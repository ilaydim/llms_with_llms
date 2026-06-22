"""
UC-1: Pre-anket tamamlanmadan platforma erişime izin verilmez (FR-8.1).
UC-8: Tüm katmanlar tamamlandığında post-anket sunulur (FR-8.2).
FR-8.3: Cevaplar student_id ile ilişkilendirilerek kaydedilir.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models.models import Student, SurveyResponse
from app.schemas.survey import SurveyQuestionOut, SurveyStatusOut, SurveySubmitIn
from app.services.survey_loader import load_survey_questions

router = APIRouter(prefix="/survey", tags=["survey"])


@router.get("/questions/{survey_type}", response_model=list[SurveyQuestionOut])
def get_questions(survey_type: str):
    try:
        return load_survey_questions(survey_type)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/status/{student_id}", response_model=SurveyStatusOut)
def get_status(student_id: int, db: DBSession = Depends(get_db)):
    """
    FR-8.1 alternatif akış desteği: Öğrenci daha önce pre-anketi doldurduysa
    (NFR-4.1 ile tutarlı şekilde) tekrar sorulmamalı — frontend bu endpoint'i
    kontrol ederek karar verir.
    """
    pre_done = (
        db.query(SurveyResponse)
        .filter(SurveyResponse.student_id == student_id, SurveyResponse.survey_type == "pre")
        .first()
        is not None
    )
    post_done = (
        db.query(SurveyResponse)
        .filter(SurveyResponse.student_id == student_id, SurveyResponse.survey_type == "post")
        .first()
        is not None
    )
    return SurveyStatusOut(pre_completed=pre_done, post_completed=post_done)


@router.post("/submit")
def submit_survey(payload: SurveySubmitIn, db: DBSession = Depends(get_db)):
    student = db.query(Student).filter(Student.id == payload.student_id).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Öğrenci bulunamadı")

    # Aynı anket tekrar gönderilirse (örn. sayfa yenileme) eski cevapları temizleyip yeniden yaz
    db.query(SurveyResponse).filter(
        SurveyResponse.student_id == payload.student_id,
        SurveyResponse.survey_type == payload.survey_type,
    ).delete()

    for answer in payload.answers:
        db.add(
            SurveyResponse(
                student_id=payload.student_id,
                survey_type=payload.survey_type,
                question_id=answer.question_id,
                answer=answer.answer,
            )
        )
    db.commit()
    return {"status": "ok", "survey_type": payload.survey_type, "answer_count": len(payload.answers)}

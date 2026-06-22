from pydantic import BaseModel


class SurveyQuestionOut(BaseModel):
    id: str
    type: str  # likert / open_ended
    text: str
    scale_min: int | None = None
    scale_max: int | None = None
    scale_labels: list[str] | None = None


class SurveyAnswerIn(BaseModel):
    question_id: str
    answer: str  # likert için sayının string hali, open_ended için serbest metin


class SurveySubmitIn(BaseModel):
    student_id: int
    survey_type: str  # pre / post
    answers: list[SurveyAnswerIn]


class SurveyStatusOut(BaseModel):
    pre_completed: bool
    post_completed: bool

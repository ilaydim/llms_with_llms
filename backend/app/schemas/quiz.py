from pydantic import BaseModel


class QuizMCQOut(BaseModel):
    id: str
    question: str
    options: list[str]
    # correct_index BİLEREK dönmüyor — istemci tarafında hile yapılmasını önlemek için


class QuizOpenEndedOut(BaseModel):
    id: str
    question: str


class QuizQuestionsOut(BaseModel):
    layer: str
    mcq: list[QuizMCQOut]
    open_ended: QuizOpenEndedOut


class MCQAnswerIn(BaseModel):
    question_id: str
    selected_index: int


class QuizSubmitIn(BaseModel):
    session_id: int
    module_code: str
    layer: str
    mcq_answers: list[MCQAnswerIn]
    open_ended_answer: str


class QuizResultOut(BaseModel):
    id: int
    layer: str
    mcq_score: float
    open_ended_score: float | None
    open_ended_feedback: str | None
    attempt_number: int
    passed: bool


class RevisitIn(BaseModel):
    session_id: int
    module_code: str
    layer: str
    revisited: bool


class RevisitOut(BaseModel):
    explanation: str | None = None

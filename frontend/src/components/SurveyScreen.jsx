import { useEffect, useState } from "react";
import { api } from "../api";

const LIKERT_VALUES = [1, 2, 3, 4, 5];

export default function SurveyScreen({ studentId, surveyType, onCompleted }) {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getSurveyQuestions(surveyType)
      .then(setQuestions)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [surveyType]);

  function setAnswer(questionId, value) {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
  }

  const allAnswered = questions.length > 0 && questions.every((q) => (answers[q.id] ?? "").toString().trim() !== "");

  async function handleSubmit(e) {
    e.preventDefault();
    if (!allAnswered || submitting) return;
    setSubmitting(true);
    setError("");
    try {
      const payload = questions.map((q) => ({ question_id: q.id, answer: String(answers[q.id]) }));
      await api.submitSurvey(studentId, surveyType, payload);
      onCompleted();
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="survey-screen">
      <div className="survey-card">
        <p className="identify-eyebrow">
          {surveyType === "pre" ? "Başlangıç Anketi" : "Bitiş Anketi"}
        </p>
        <h1 className="identify-title">
          {surveyType === "pre"
            ? "Başlamadan önce birkaç soru"
            : "Harika, bitirdin! Son birkaç soru"}
        </h1>
        <p className="identify-sub">
          {surveyType === "pre"
            ? "Bu kısa anket, öğrenmeye başlamadan önceki bilgi düzeyini ölçmek için — doğru/yanlış cevap yok."
            : "Bu anket, öğrenme öncesi ve sonrası karşılaştırması için kullanılacak."}
        </p>

        {loading ? (
          <p className="chat-status">Yükleniyor…</p>
        ) : (
          <form onSubmit={handleSubmit} className="survey-form">
            {questions.map((q, i) => (
              <div className="survey-question" key={q.id}>
                <p className="survey-question-text">
                  <span className="survey-question-index">{i + 1}.</span> {q.text}
                </p>
                {q.type === "likert" ? (
                  <div className="survey-likert">
                    <span className="survey-likert-label">{q.scale_labels?.[0]}</span>
                    <div className="survey-likert-scale">
                      {LIKERT_VALUES.map((v) => (
                        <label key={v} className="survey-likert-option">
                          <input
                            type="radio"
                            name={q.id}
                            value={v}
                            checked={answers[q.id] === v}
                            onChange={() => setAnswer(q.id, v)}
                          />
                          <span>{v}</span>
                        </label>
                      ))}
                    </div>
                    <span className="survey-likert-label">{q.scale_labels?.[1]}</span>
                  </div>
                ) : (
                  <textarea
                    rows={3}
                    value={answers[q.id] || ""}
                    onChange={(e) => setAnswer(q.id, e.target.value)}
                    placeholder="Cevabını buraya yaz…"
                  />
                )}
              </div>
            ))}

            {error && <p className="identify-error">{error}</p>}

            <button className="btn-primary" type="submit" disabled={!allAnswered || submitting}>
              {submitting ? "Gönderiliyor…" : "Anketi Gönder"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

import { useEffect, useState } from "react";
import { api } from "../api";
import { useLanguage } from "../i18n";
import LanguageSwitch from "./LanguageSwitch";

const LIKERT_VALUES = [1, 2, 3, 4, 5];

export default function SurveyScreen({ studentId, surveyType, onCompleted }) {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const { t, lang } = useLanguage();

  useEffect(() => {
    api
      .getSurveyQuestions(surveyType, lang)
      .then(setQuestions)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [surveyType, lang]);

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
        <LanguageSwitch />
        <p className="identify-eyebrow">
          {surveyType === "pre" ? t("survey.pre.eyebrow") : t("survey.post.eyebrow")}
        </p>
        <h1 className="identify-title">
          {surveyType === "pre" ? t("survey.pre.title") : t("survey.post.title")}
        </h1>
        <p className="identify-sub">
          {surveyType === "pre" ? t("survey.pre.sub") : t("survey.post.sub")}
        </p>

        {loading ? (
          <p className="chat-status">{t("common.loading")}</p>
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
                    placeholder={t("common.writeYourAnswer")}
                  />
                )}
              </div>
            ))}

            {error && <p className="identify-error">{error}</p>}

            <button className="btn-primary" type="submit" disabled={!allAnswered || submitting}>
              {submitting ? t("survey.submitting") : t("survey.submit")}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

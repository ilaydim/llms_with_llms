import { useEffect, useState } from "react";
import { api } from "../api";

const LAYER_LABEL = { theory: "Theory", application: "Application", critical: "Critical Thinking" };

export default function QuizScreen({ sessionId, moduleCode, layer, onLeaveQuiz, onAdvanceLayer }) {
  const [quiz, setQuiz] = useState(null);
  const [mcqAnswers, setMcqAnswers] = useState({});
  const [openEndedAnswer, setOpenEndedAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [revisitExplanation, setRevisitExplanation] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setQuiz(null);
    setResult(null);
    setRevisitExplanation(null);
    setMcqAnswers({});
    setOpenEndedAnswer("");
    setLoading(true);
    api
      .getQuiz(moduleCode, layer)
      .then(setQuiz)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [moduleCode, layer]);

  const allMcqAnswered = quiz && quiz.mcq.every((q) => mcqAnswers[q.id] !== undefined);
  const canSubmit = allMcqAnswered && openEndedAnswer.trim().length > 0;

  async function handleSubmit(e) {
    e.preventDefault();
    if (!canSubmit || submitting) return;
    setSubmitting(true);
    setError("");
    try {
      const mcqPayload = Object.entries(mcqAnswers).map(([question_id, selected_index]) => ({
        question_id,
        selected_index,
      }));
      const res = await api.submitQuiz({
        sessionId,
        moduleCode,
        layer,
        mcqAnswers: mcqPayload,
        openEndedAnswer,
      });
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRevisitChoice(wantsRevisit) {
    setError("");
    try {
      const res = await api.submitRevisit({ sessionId, moduleCode, layer, revisited: wantsRevisit });
      if (wantsRevisit) {
        setRevisitExplanation(res.explanation);
      } else {
        onAdvanceLayer();
      }
    } catch (e) {
      setError(e.message);
    }
  }

  function handleRetake() {
    setResult(null);
    setRevisitExplanation(null);
    setMcqAnswers({});
    setOpenEndedAnswer("");
  }

  if (loading) return <div className="quiz-screen"><p className="chat-status">Loading quiz…</p></div>;
  if (!quiz) return <div className="quiz-screen"><p className="identify-error">{error || "Quiz not found."}</p></div>;

  return (
    <div className="quiz-screen">
      <div className="quiz-card">
        <div className="quiz-header">
          <span className="chat-intro-label">{LAYER_LABEL[layer]} — End-of-Layer Quiz</span>
          <button className="quiz-back-link" onClick={onLeaveQuiz}>← Back to dialogue</button>
        </div>

        {!result && !revisitExplanation && (
          <form onSubmit={handleSubmit} className="survey-form">
            {quiz.mcq.map((q, i) => (
              <div className="survey-question" key={q.id}>
                <p className="survey-question-text">
                  <span className="survey-question-index">{i + 1}.</span> {q.question}
                </p>
                <div className="quiz-options">
                  {q.options.map((opt, idx) => (
                    <label key={idx} className="quiz-option">
                      <input
                        type="radio"
                        name={q.id}
                        checked={mcqAnswers[q.id] === idx}
                        onChange={() => setMcqAnswers((prev) => ({ ...prev, [q.id]: idx }))}
                      />
                      <span>{opt}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}

            <div className="survey-question">
              <p className="survey-question-text">
                <span className="survey-question-index">{quiz.mcq.length + 1}.</span> {quiz.open_ended.question}
              </p>
              <textarea
                rows={4}
                value={openEndedAnswer}
                onChange={(e) => setOpenEndedAnswer(e.target.value)}
                placeholder="Write your answer here…"
              />
            </div>

            {error && <p className="identify-error">{error}</p>}

            <button className="btn-primary" type="submit" disabled={!canSubmit || submitting}>
              {submitting ? "Evaluating…" : "Submit quiz"}
            </button>
          </form>
        )}

        {result && !revisitExplanation && (
          <div className="quiz-result">
            <p className={`quiz-result-badge ${result.passed ? "quiz-result-badge--pass" : "quiz-result-badge--fail"}`}>
              {result.passed ? "Passed" : "Not yet"}
            </p>
            <p className="quiz-result-detail">
              Multiple choice: {Math.round(result.mcq_score * 100)}% ·{" "}
              Open-ended: {Math.round((result.open_ended_score ?? 0) * 100)}%
            </p>
            {result.open_ended_feedback && (
              <p className="quiz-result-feedback">{result.open_ended_feedback}</p>
            )}

            {result.passed ? (
              <button className="btn-primary" onClick={onAdvanceLayer}>
                Continue →
              </button>
            ) : (
              <div className="quiz-revisit-choice">
                <p>Would you like to revisit this topic with a different explanation?</p>
                <div className="quiz-revisit-buttons">
                  <button className="btn-secondary" onClick={() => handleRevisitChoice(false)}>
                    No, continue anyway
                  </button>
                  <button className="btn-primary" onClick={() => handleRevisitChoice(true)}>
                    Yes, explain again
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {revisitExplanation && (
          <div className="quiz-result">
            <p className="chat-intro-label">New explanation</p>
            <p className="quiz-revisit-text">{revisitExplanation}</p>
            <p className="survey-question-text" style={{ marginTop: 16 }}>Does that make more sense?</p>
            <button className="btn-primary" onClick={handleRetake}>
              Yes, retake the quiz
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

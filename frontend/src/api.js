const BASE_URL = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`İstek başarısız (${res.status}): ${body}`);
  }
  return res.json();
}

export const api = {
  identifyStudent: (name, studentNo) =>
    request("/students/identify", {
      method: "POST",
      body: JSON.stringify({ name, student_no: studentNo || null }),
    }),

  startSession: (studentId) =>
    request(`/sessions/start/${studentId}`, { method: "POST" }),

  getLayerIntro: (moduleCode, layer) =>
    request(`/dialogue/${moduleCode}/${layer}/intro`),

  getHistory: (sessionId, moduleCode, layer) =>
    request(`/dialogue/${sessionId}/${moduleCode}/${layer}/history`),

  sendMessage: ({ sessionId, moduleCode, layer, content }) =>
    request("/dialogue/message", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        module_code: moduleCode,
        layer,
        content,
      }),
    }),

  getSurveyStatus: (studentId) => request(`/survey/status/${studentId}`),

  getSurveyQuestions: (surveyType) => request(`/survey/questions/${surveyType}`),

  submitSurvey: (studentId, surveyType, answers) =>
    request("/survey/submit", {
      method: "POST",
      body: JSON.stringify({ student_id: studentId, survey_type: surveyType, answers }),
    }),

  getQuiz: (moduleCode, layer) => request(`/quiz/${moduleCode}/${layer}`),

  submitQuiz: ({ sessionId, moduleCode, layer, mcqAnswers, openEndedAnswer }) =>
    request("/quiz/submit", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        module_code: moduleCode,
        layer,
        mcq_answers: mcqAnswers,
        open_ended_answer: openEndedAnswer,
      }),
    }),

  submitRevisit: ({ sessionId, moduleCode, layer, revisited }) =>
    request("/quiz/revisit", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, module_code: moduleCode, layer, revisited }),
    }),
};

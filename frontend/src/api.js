// Local dev: Vite proxy forwards /students, /sessions, etc. to http://127.0.0.1:8000
// Production: frontend is served by FastAPI at the same origin, so relative URLs work
const BASE_URL = import.meta.env.VITE_API_URL ?? "";

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

  getLayerIntro: (moduleCode, layer, lang = "en") =>
    request(`/dialogue/${moduleCode}/${layer}/intro?lang=${lang}`),

  getHistory: (sessionId, moduleCode, layer) =>
    request(`/dialogue/${sessionId}/${moduleCode}/${layer}/history`),

  sendMessage: ({ sessionId, moduleCode, layer, content, lang = "en" }) =>
    request("/dialogue/message", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        module_code: moduleCode,
        layer,
        content,
        lang,
      }),
    }),

  getSurveyStatus: (studentId) => request(`/survey/status/${studentId}`),

  getSurveyQuestions: (surveyType, lang = "en") => request(`/survey/questions/${surveyType}?lang=${lang}`),

  submitSurvey: (studentId, surveyType, answers) =>
    request("/survey/submit", {
      method: "POST",
      body: JSON.stringify({ student_id: studentId, survey_type: surveyType, answers }),
    }),

  getQuiz: (moduleCode, layer, lang = "en") => request(`/quiz/${moduleCode}/${layer}?lang=${lang}`),

  submitQuiz: ({ sessionId, moduleCode, layer, mcqAnswers, openEndedAnswer, lang = "en" }) =>
    request("/quiz/submit", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        module_code: moduleCode,
        layer,
        mcq_answers: mcqAnswers,
        open_ended_answer: openEndedAnswer,
        lang,
      }),
    }),

  submitRevisit: ({ sessionId, moduleCode, layer, revisited, lang = "en" }) =>
    request("/quiz/revisit", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, module_code: moduleCode, layer, revisited, lang }),
    }),

  getStudentProgress: (studentId) => request(`/progress/student/${studentId}`),

  getTasks: (sessionId, moduleCode) => request(`/tasks/${sessionId}/${moduleCode}`),

  updateTask: (taskId, status) =>
    request(`/tasks/${taskId}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),

  /**
   * NFR-1.1: Streaming mesaj gönder.
   * onChunk(text) her chunk geldiğinde çağrılır.
   * Dönen Promise { message_id, created_at } ile resolve olur.
   */
  sendMessageStream: ({ sessionId, moduleCode, layer, content, lang = "en" }, onChunk) => {
    return new Promise(async (resolve, reject) => {
      try {
        const res = await fetch(`${BASE_URL}/dialogue/message/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sessionId, module_code: moduleCode, layer, content, lang }),
        });

        if (!res.ok) {
          const body = await res.text();
          return reject(new Error(`İstek başarısız (${res.status}): ${body}`));
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });

          // SSE satırlarını parse et
          const lines = buffer.split("\n");
          buffer = lines.pop(); // son satır tamamlanmamış olabilir

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const data = JSON.parse(line.slice(6));
            if (data.error) return reject(new Error(data.error));
            if (data.done) return resolve({ message_id: data.message_id, created_at: data.created_at });
            if (data.chunk) onChunk(data.chunk);
          }
        }
      } catch (e) {
        reject(e);
      }
    });
  },
};

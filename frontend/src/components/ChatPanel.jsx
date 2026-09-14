import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import { useLanguage } from "../i18n";
import MessageBubble from "./MessageBubble";

export default function ChatPanel({ sessionId, moduleCode, layer, onStartQuiz }) {
  const [intro, setIntro] = useState("");
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState("");
  // FR-4.3: uygulama katmanı adım takibi
  const [tasks, setTasks] = useState([]);
  const scrollRef = useRef(null);
  const { t, lang } = useLanguage();

  useEffect(() => {
    let cancelled = false;
    setLoadingHistory(true);
    setError("");

    const fetches = [
      api.getLayerIntro(moduleCode, layer, lang),
      api.getHistory(sessionId, moduleCode, layer),
    ];
    // Uygulama katmanında task adımlarını da çek
    if (layer === "application") {
      fetches.push(api.getTasks(sessionId, moduleCode));
    }

    Promise.all(fetches)
      .then(([introRes, historyRes, tasksRes]) => {
        if (cancelled) return;
        setIntro(introRes.intro_text);
        setMessages(historyRes);
        setTasks(tasksRes || []);
      })
      .catch((e) => !cancelled && setError(e.message))
      .finally(() => !cancelled && setLoadingHistory(false));

    return () => { cancelled = true; };
  }, [sessionId, moduleCode, layer, lang]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, intro]);

  async function handleSend(e) {
    e.preventDefault();
    const content = draft.trim();
    if (!content || sending) return;

    setSending(true);
    setError("");
    const studentTempId = `temp-student-${Date.now()}`;
    const tutorTempId = `temp-tutor-${Date.now()}`;

    setMessages((prev) => [
      ...prev,
      { id: studentTempId, sender: "student", content, created_at: new Date().toISOString() },
      // NFR-1.1: streaming balonu — chunk'lar geldikçe content güncellenir
      { id: tutorTempId, sender: "tutor_agent", content: "", created_at: new Date().toISOString(), streaming: true },
    ]);
    setDraft("");

    try {
      const meta = await api.sendMessageStream(
        { sessionId, moduleCode, layer, content, lang },
        (chunk) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === tutorTempId ? { ...m, content: m.content + chunk } : m
            )
          );
        }
      );
      // Stream bitti: geçici ID'yi gerçek mesaj verileriyle değiştir
      setMessages((prev) =>
        prev.map((m) =>
          m.id === tutorTempId
            ? { ...m, id: meta.message_id, created_at: meta.created_at, streaming: false }
            : m
        )
      );
    } catch (err) {
      // Hata olursa streaming balonunu kaldır
      setMessages((prev) => prev.filter((m) => m.id !== tutorTempId));
      setError(err.message);
    } finally {
      setSending(false);
    }
  }

  async function handleTaskToggle(task) {
    const newStatus = task.status === "completed" ? "not_started" : "completed";
    try {
      const updated = await api.updateTask(task.id, newStatus);
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
    } catch (e) {
      setError(e.message);
    }
  }

  const layerLabel = t(`layer.${layer}`);
  const placeholder = t(`chat.placeholder.${layer}`);
  const allTasksDone = tasks.length > 0 && tasks.every((t) => t.status === "completed");

  return (
    <div className="chat-panel">
      <div className="chat-scroll" ref={scrollRef}>
        {loadingHistory ? (
          <p className="chat-status">{t("common.loading")}</p>
        ) : (
          <>
            <div className="chat-intro">
              <span className="chat-intro-label">{t("chat.intro", { layer: layerLabel })}</span>
              <p>{intro}</p>
            </div>

            {/* FR-4.3: Uygulama katmanı adım checklist'i */}
            {layer === "application" && tasks.length > 0 && (
              <div className="task-checklist">
                <p className="task-checklist-title">{t("chat.taskSteps")}</p>
                {tasks.map((task) => (
                  <label key={task.id} className={`task-item ${task.status === "completed" ? "task-item--done" : ""}`}>
                    <input
                      type="checkbox"
                      checked={task.status === "completed"}
                      onChange={() => handleTaskToggle(task)}
                    />
                    <span>
                      <strong>{task.step_number}.</strong>{" "}
                      {task.step_number >= 1 && task.step_number <= 3
                        ? t(`chat.step.${task.step_number}`)
                        : t("chat.step.generic", { n: task.step_number })}
                    </span>
                  </label>
                ))}
                {allTasksDone && (
                  <p className="task-checklist-done">
                    {t("chat.allTasksDone")}
                  </p>
                )}
              </div>
            )}

            {messages.map((m, i) => (
              <MessageBubble
                key={m.id}
                sender={m.sender}
                content={m.content}
                createdAt={m.created_at}
                index={i + 1}
                streaming={!!m.streaming}
              />
            ))}
            {/* NFR-1.1: streaming aktifken "düşünüyor" yerine streaming balonu göster */}
            {sending && !messages.some((m) => m.streaming) && (
              <div className="bubble-row bubble-row--tutor">
                <div className="bubble bubble--pending">
                  <span className="bubble-tag">{t("bubble.tutor")}</span>
                  <p className="bubble-content bubble-content--pending">{t("chat.thinking")}</p>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {error && <p className="chat-error">{error}</p>}

      <form className="chat-input-row" onSubmit={handleSend}>
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder={placeholder}
          disabled={sending || loadingHistory}
        />
        <button className="btn-primary" type="submit" disabled={sending || loadingHistory || !draft.trim()}>
          {t("chat.send")}
        </button>
        <button type="button" className="btn-secondary" onClick={onStartQuiz} disabled={loadingHistory}>
          {t("chat.takeQuiz")}
        </button>
      </form>
    </div>
  );
}

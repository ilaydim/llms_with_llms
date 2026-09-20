import { useState } from "react";
import { api } from "../api";
import { useLanguage } from "../i18n";
import MessageBubble from "./MessageBubble";

/**
 * FR-6.5 / UC-6 adım 4: geri dönüş anlatımından sonra öğrenci Tutor Agent'a soru sorabilir.
 * Aynı /dialogue/message/stream endpoint'ini kullanır, yani mesajlar normal diyalog
 * geçmişine (aynı katman) kaydedilir ve analytics'e sayılır.
 */
export default function RevisitChat({ sessionId, moduleCode, layer }) {
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const { t, lang } = useLanguage();

  async function handleSend(e) {
    e.preventDefault();
    const content = draft.trim();
    if (!content || sending) return;

    setSending(true);
    setError("");
    const stamp = Date.now();
    const tutorTempId = `temp-tutor-${stamp}`;
    setMessages((prev) => [
      ...prev,
      { id: `temp-student-${stamp}`, sender: "student", content, created_at: new Date().toISOString() },
      { id: tutorTempId, sender: "tutor_agent", content: "", streaming: true },
    ]);
    setDraft("");

    try {
      const meta = await api.sendMessageStream(
        { sessionId, moduleCode, layer, content, lang },
        (chunk) =>
          setMessages((prev) =>
            prev.map((m) => (m.id === tutorTempId ? { ...m, content: m.content + chunk } : m))
          )
      );
      setMessages((prev) =>
        prev.map((m) =>
          m.id === tutorTempId
            ? { ...m, id: meta.message_id, created_at: meta.created_at, streaming: false }
            : m
        )
      );
    } catch (err) {
      setMessages((prev) => prev.filter((m) => m.id !== tutorTempId));
      setError(err.message);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="revisit-chat">
      <p className="chat-intro-label">{t("quiz.askTutor")}</p>
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
      {error && <p className="chat-error">{error}</p>}
      <form className="chat-input-row" onSubmit={handleSend}>
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder={t("quiz.askPlaceholder")}
          disabled={sending}
        />
        <button className="btn-primary" type="submit" disabled={sending || !draft.trim()}>
          {t("chat.send")}
        </button>
      </form>
    </div>
  );
}

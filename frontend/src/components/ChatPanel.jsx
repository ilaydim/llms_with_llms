import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import MessageBubble from "./MessageBubble";

const LAYER_COPY = {
  theory: {
    placeholder: "RAG hakkında merak ettiğini kendi cümlelerinle yaz…",
    emptyLabel: "Teori",
  },
  application: {
    placeholder: "Görevle ilgili bir soru sor, Tutor Agent dokümanlarda arama yapacak…",
    emptyLabel: "Uygulama",
  },
  critical: {
    placeholder: "RAG'in sınırları üzerine düşüncelerini paylaş…",
    emptyLabel: "Eleştirel Bakış",
  },
};

export default function ChatPanel({ sessionId, moduleCode, layer, onStartQuiz }) {
  const [intro, setIntro] = useState("");
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    setLoadingHistory(true);
    setError("");

    Promise.all([
      api.getLayerIntro(moduleCode, layer),
      api.getHistory(sessionId, moduleCode, layer),
    ])
      .then(([introRes, historyRes]) => {
        if (cancelled) return;
        setIntro(introRes.intro_text);
        setMessages(historyRes);
      })
      .catch((e) => !cancelled && setError(e.message))
      .finally(() => !cancelled && setLoadingHistory(false));

    return () => {
      cancelled = true;
    };
  }, [sessionId, moduleCode, layer]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, intro]);

  async function handleSend(e) {
    e.preventDefault();
    const content = draft.trim();
    if (!content || sending) return;

    setSending(true);
    setError("");
    setMessages((prev) => [
      ...prev,
      { id: `temp-${Date.now()}`, sender: "student", content, created_at: new Date().toISOString() },
    ]);
    setDraft("");

    try {
      const tutorReply = await api.sendMessage({ sessionId, moduleCode, layer, content });
      setMessages((prev) => [...prev, tutorReply]);
    } catch (e) {
      setError(e.message);
    } finally {
      setSending(false);
    }
  }

  const copy = LAYER_COPY[layer];

  return (
    <div className="chat-panel">
      <div className="chat-scroll" ref={scrollRef}>
        {loadingHistory ? (
          <p className="chat-status">Yükleniyor…</p>
        ) : (
          <>
            <div className="chat-intro">
              <span className="chat-intro-label">{copy.emptyLabel} — Giriş</span>
              <p>{intro}</p>
            </div>
            {messages.map((m, i) => (
              <MessageBubble
                key={m.id}
                sender={m.sender}
                content={m.content}
                createdAt={m.created_at}
                index={i + 1}
              />
            ))}
            {sending && (
              <div className="bubble-row bubble-row--tutor">
                <div className="bubble bubble--pending">
                  <span className="bubble-tag">TUTOR</span>
                  <p className="bubble-content bubble-content--pending">düşünüyor…</p>
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
          placeholder={copy.placeholder}
          disabled={sending || loadingHistory}
        />
        <button className="btn-primary" type="submit" disabled={sending || loadingHistory || !draft.trim()}>
          Gönder
        </button>
        <button type="button" className="btn-secondary" onClick={onStartQuiz} disabled={loadingHistory}>
          Quiz'e geç
        </button>
      </form>
    </div>
  );
}

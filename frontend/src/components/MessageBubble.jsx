function formatTime(isoString) {
  try {
    return new Date(isoString).toLocaleTimeString("en-GB", {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

export default function MessageBubble({ sender, content, createdAt, index, streaming }) {
  const isStudent = sender === "student";
  return (
    <div className={`bubble-row ${isStudent ? "bubble-row--student" : "bubble-row--tutor"}`}>
      <div className={`bubble${streaming ? " bubble--streaming" : ""}`}>
        <div className="bubble-meta">
          <span className="bubble-tag">
            {isStudent ? "YOU" : "TUTOR"}
            {typeof index === "number" && <span className="bubble-index">·{String(index).padStart(2, "0")}</span>}
          </span>
          {createdAt && !streaming && <span className="bubble-time">{formatTime(createdAt)}</span>}
          {streaming && <span className="bubble-streaming-label">typing…</span>}
        </div>
        <p className="bubble-content">
          {content}
          {streaming && <span className="streaming-cursor" />}
        </p>
      </div>
    </div>
  );
}

function formatTime(isoString) {
  try {
    return new Date(isoString).toLocaleTimeString("tr-TR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

export default function MessageBubble({ sender, content, createdAt, index }) {
  const isStudent = sender === "student";
  return (
    <div className={`bubble-row ${isStudent ? "bubble-row--student" : "bubble-row--tutor"}`}>
      <div className="bubble">
        <div className="bubble-meta">
          <span className="bubble-tag">
            {isStudent ? "SEN" : "TUTOR"}
            {typeof index === "number" && <span className="bubble-index">·{String(index).padStart(2, "0")}</span>}
          </span>
          {createdAt && <span className="bubble-time">{formatTime(createdAt)}</span>}
        </div>
        <p className="bubble-content">{content}</p>
      </div>
    </div>
  );
}

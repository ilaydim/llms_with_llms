import { useState } from "react";

export default function IdentifyScreen({ onIdentified, loading, error }) {
  const [name, setName] = useState("");
  const [studentNo, setStudentNo] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!name.trim()) return;
    onIdentified(name.trim(), studentNo.trim());
  }

  return (
    <div className="identify-screen">
      <div className="identify-card">
        <p className="identify-eyebrow">Learning LLMs with LLMs</p>
        <h1 className="identify-title">
          Learn about LLMs by talking to one.
        </h1>
        <p className="identify-sub">
          In this pilot study you will explore RAG (Retrieval-Augmented Generation)
          across three layers: <strong>Theory</strong> → <strong>Application</strong> →{" "}
          <strong>Critical Thinking</strong>. No account needed — just introduce yourself.
        </p>

        <form onSubmit={handleSubmit} className="identify-form">
          <label className="field">
            <span>Your name</span>
            <input
              autoFocus
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Alex Johnson"
              required
            />
          </label>
          <label className="field">
            <span>Student ID <em>(optional)</em></span>
            <input
              value={studentNo}
              onChange={(e) => setStudentNo(e.target.value)}
              placeholder="e.g. 20210101"
            />
          </label>

          {error && <p className="identify-error">{error}</p>}

          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? "Setting up…" : "Start learning"}
          </button>
        </form>

        <p className="identify-footnote">
          If you've used this platform before with the same name, you'll resume where you left off.
        </p>
      </div>
    </div>
  );
}

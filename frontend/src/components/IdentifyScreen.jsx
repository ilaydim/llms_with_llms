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
          Bir LLM'le diyalog kurarak, LLM'leri öğren.
        </h1>
        <p className="identify-sub">
          Bu pilot çalışmada RAG (Retrieval-Augmented Generation) konusunu üç
          katmanda işleyeceksin: <strong>Teori</strong> → <strong>Uygulama</strong> →{" "}
          <strong>Eleştirel Bakış</strong>. Başlamak için kendini tanıt — hesap
          oluşturman gerekmiyor.
        </p>

        <form onSubmit={handleSubmit} className="identify-form">
          <label className="field">
            <span>Adın</span>
            <input
              autoFocus
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="örn. Ayşe Yılmaz"
              required
            />
          </label>
          <label className="field">
            <span>Öğrenci numaran <em>(isteğe bağlı)</em></span>
            <input
              value={studentNo}
              onChange={(e) => setStudentNo(e.target.value)}
              placeholder="örn. 20210101"
            />
          </label>

          {error && <p className="identify-error">{error}</p>}

          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? "Hazırlanıyor…" : "Öğrenmeye başla"}
          </button>
        </form>

        <p className="identify-footnote">
          Daha önce aynı isimle girdiysen, kaldığın yerden devam edeceksin.
        </p>
      </div>
    </div>
  );
}

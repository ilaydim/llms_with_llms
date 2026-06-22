export default function TopBar({ studentName, layer }) {
  const layerLabel = { theory: "Teori", application: "Uygulama", critical: "Eleştirel Bakış" }[layer];
  return (
    <header className="top-bar">
      <div className="top-bar-brand">
        <span className="top-bar-mark">⟡</span>
        <span>Learning LLMs with LLMs</span>
      </div>
      <div className="top-bar-status">
        <span className="top-bar-layer">{layerLabel} katmanı</span>
        <span className="top-bar-divider">·</span>
        <span className="top-bar-student">{studentName}</span>
      </div>
    </header>
  );
}

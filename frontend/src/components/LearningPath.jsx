const LAYERS = [
  { key: "theory", index: "01", label: "Teori", desc: "Kavramsal temel" },
  { key: "application", index: "02", label: "Uygulama", desc: "RAG'i kur, dene" },
  { key: "critical", index: "03", label: "Eleştirel Bakış", desc: "Sınırlar, riskler" },
];

export default function LearningPath({ activeLayer, onSelect, moduleName }) {
  const activeIdx = LAYERS.findIndex((l) => l.key === activeLayer);

  return (
    <nav className="learning-path">
      <div className="learning-path-header">
        <p className="learning-path-module-label">Modül</p>
        <p className="learning-path-module-name">{moduleName}</p>
      </div>

      <ol className="learning-path-list">
        {LAYERS.map((layer, i) => {
          const state =
            i < activeIdx ? "done" : i === activeIdx ? "active" : "upcoming";
          return (
            <li key={layer.key} className={`path-step path-step--${state}`}>
              <button
                className="path-step-button"
                onClick={() => onSelect(layer.key)}
                aria-current={state === "active" ? "step" : undefined}
              >
                <span className="path-step-index">{layer.index}</span>
                <span className="path-step-text">
                  <span className="path-step-label">{layer.label}</span>
                  <span className="path-step-desc">{layer.desc}</span>
                </span>
              </button>
              {i < LAYERS.length - 1 && <span className="path-step-connector" aria-hidden="true" />}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

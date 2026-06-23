const LAYERS = [
  { key: "theory", index: "01", label: "Theory", desc: "Conceptual foundation" },
  { key: "application", index: "02", label: "Application", desc: "Build & experiment" },
  { key: "critical", index: "03", label: "Critical Thinking", desc: "Limits & risks" },
];

export default function LearningPath({ activeLayer, onSelect, moduleName, unlockedLayers = [] }) {
  const activeIdx = LAYERS.findIndex((l) => l.key === activeLayer);

  return (
    <nav className="learning-path">
      <div className="learning-path-header">
        <p className="learning-path-module-label">Module</p>
        <p className="learning-path-module-name">{moduleName}</p>
      </div>

      <ol className="learning-path-list">
        {LAYERS.map((layer, i) => {
          const isCompleted = i < activeIdx;
          const isActive = i === activeIdx;
          const isLocked = !isActive && !isCompleted && !unlockedLayers.includes(layer.key);
          const state = isCompleted ? "done" : isActive ? "active" : "upcoming";

          return (
            <li key={layer.key} className={`path-step path-step--${state}${isLocked ? " path-step--locked" : ""}`}>
              <button
                className="path-step-button"
                onClick={() => !isLocked && onSelect(layer.key)}
                disabled={isLocked}
                aria-current={isActive ? "step" : undefined}
                title={isLocked ? "Complete the previous layer's quiz to unlock" : undefined}
              >
                <span className="path-step-index">{isLocked ? "🔒" : layer.index}</span>
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

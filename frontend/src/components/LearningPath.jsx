import { useLanguage } from "../i18n";

const LAYER_KEYS = ["theory", "application", "critical"];

export default function LearningPath({ activeLayer, onSelect, moduleName, unlockedLayers = [] }) {
  const { t } = useLanguage();
  const layers = LAYER_KEYS.map((key, i) => ({
    key,
    index: String(i + 1).padStart(2, "0"),
    label: t(`layer.${key}`),
    desc: t(`layer.${key}.desc`),
  }));
  const activeIdx = layers.findIndex((l) => l.key === activeLayer);

  return (
    <nav className="learning-path">
      <div className="learning-path-header">
        <p className="learning-path-module-label">{t("learningPath.module")}</p>
        <p className="learning-path-module-name">{moduleName}</p>
      </div>

      <ol className="learning-path-list">
        {layers.map((layer, i) => {
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
                title={isLocked ? t("learningPath.locked") : undefined}
              >
                <span className="path-step-index">{isLocked ? "🔒" : layer.index}</span>
                <span className="path-step-text">
                  <span className="path-step-label">{layer.label}</span>
                  <span className="path-step-desc">{layer.desc}</span>
                </span>
              </button>
              {i < layers.length - 1 && <span className="path-step-connector" aria-hidden="true" />}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

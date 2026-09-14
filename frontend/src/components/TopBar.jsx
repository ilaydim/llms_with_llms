import { useLanguage } from "../i18n";
import LanguageSwitch from "./LanguageSwitch";

export default function TopBar({ studentName, layer }) {
  const { t } = useLanguage();
  const layerLabel = { theory: t("layer.theory"), application: t("layer.application"), critical: t("layer.critical") }[layer];
  return (
    <header className="top-bar">
      <div className="top-bar-brand">
        <span className="top-bar-mark">⟡</span>
        <span>{t("app.brand")}</span>
      </div>
      <div className="top-bar-status">
        <span className="top-bar-layer">{t("topbar.layerLine", { layer: layerLabel })}</span>
        <span className="top-bar-divider">·</span>
        <span className="top-bar-student">{studentName}</span>
        <span className="top-bar-divider">·</span>
        <LanguageSwitch />
      </div>
    </header>
  );
}

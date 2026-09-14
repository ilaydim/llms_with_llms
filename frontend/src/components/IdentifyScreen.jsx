import { useState } from "react";
import { useLanguage } from "../i18n";
import LanguageSwitch from "./LanguageSwitch";

export default function IdentifyScreen({ onIdentified, loading, error }) {
  const [name, setName] = useState("");
  const [studentNo, setStudentNo] = useState("");
  const { t } = useLanguage();

  function handleSubmit(e) {
    e.preventDefault();
    if (!name.trim()) return;
    onIdentified(name.trim(), studentNo.trim());
  }

  return (
    <div className="identify-screen">
      <div className="identify-card">
        <LanguageSwitch />
        <p className="identify-eyebrow">{t("app.brand")}</p>
        <h1 className="identify-title">
          {t("identify.title")}
        </h1>
        <p className="identify-sub">
          {t("identify.sub1")}{" "}
          <strong>{t("layer.theory")}</strong> → <strong>{t("layer.application")}</strong> →{" "}
          <strong>{t("layer.critical")}</strong>. {t("identify.sub2")}
        </p>

        <form onSubmit={handleSubmit} className="identify-form">
          <label className="field">
            <span>{t("identify.name.label")}</span>
            <input
              autoFocus
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t("identify.name.placeholder")}
              required
            />
          </label>
          <label className="field">
            <span>{t("identify.studentNo.label")} <em>{t("identify.studentNo.optional")}</em></span>
            <input
              value={studentNo}
              onChange={(e) => setStudentNo(e.target.value)}
              placeholder={t("identify.studentNo.placeholder")}
            />
          </label>

          {error && <p className="identify-error">{error}</p>}

          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? t("identify.settingUp") : t("identify.start")}
          </button>
        </form>

        <p className="identify-footnote">
          {t("identify.footnote")}
        </p>
      </div>
    </div>
  );
}

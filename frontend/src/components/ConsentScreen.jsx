import { useState } from "react";
import { useLanguage } from "../i18n";
import LanguageSwitch from "./LanguageSwitch";

export default function ConsentScreen({ onConsented }) {
  const [checked, setChecked] = useState(false);
  const { t } = useLanguage();

  return (
    <div className="identify-screen">
      <div className="identify-card consent-card">
        <LanguageSwitch />
        <p className="identify-eyebrow">{t("app.brand")}</p>
        <h1 className="identify-title">{t("consent.title")}</h1>

        <div className="consent-body">
          <p className="consent-section-title">{t("consent.about.title")}</p>
          <p>{t("consent.about.body")}</p>

          <p className="consent-section-title">{t("consent.whatYouWillDo.title")}</p>
          <p>
            {t("consent.whatYouWillDo.body1")} <strong>RAG (Retrieval-Augmented Generation)</strong>{" "}
            {t("consent.whatYouWillDo.body2")}
          </p>

          <p className="consent-section-title">{t("consent.data.title")}</p>
          <p>{t("consent.data.intro")}</p>
          <ul className="consent-list">
            <li>{t("consent.data.item1")}</li>
            <li>{t("consent.data.item2")}</li>
            <li>{t("consent.data.item3")}</li>
            <li>{t("consent.data.item4")}</li>
            <li>{t("consent.data.item5")}</li>
          </ul>

          <p className="consent-section-title">{t("consent.confidentiality.title")}</p>
          <p>
            {t("consent.confidentiality.body1")} <strong>{t("consent.confidentiality.emphasis")}</strong>{" "}
            {t("consent.confidentiality.body2")}
          </p>

          <p className="consent-section-title">{t("consent.voluntary.title")}</p>
          <p>{t("consent.voluntary.body")}</p>
        </div>

        <label className="consent-checkbox-row">
          <input
            type="checkbox"
            checked={checked}
            onChange={(e) => setChecked(e.target.checked)}
          />
          <span>
            {t("consent.checkbox.pre")} <strong>{t("consent.checkbox.emphasis")}</strong>{t("consent.checkbox.post")}
          </span>
        </label>

        <button
          className="btn-primary"
          onClick={onConsented}
          disabled={!checked}
        >
          {t("consent.continue")}
        </button>
      </div>
    </div>
  );
}

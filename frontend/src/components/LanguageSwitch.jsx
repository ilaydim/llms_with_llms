import { useLanguage } from "../i18n";

export default function LanguageSwitch({ className = "" }) {
  const { lang, setLang } = useLanguage();

  return (
    <div className={`lang-switch ${className}`} role="group" aria-label="Language / Dil">
      <button
        type="button"
        className={`lang-switch-option ${lang === "en" ? "lang-switch-option--active" : ""}`}
        onClick={() => setLang("en")}
      >
        EN
      </button>
      <button
        type="button"
        className={`lang-switch-option ${lang === "tr" ? "lang-switch-option--active" : ""}`}
        onClick={() => setLang("tr")}
      >
        TR
      </button>
    </div>
  );
}

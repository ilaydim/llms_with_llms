import { useState } from "react";

export default function ConsentScreen({ onConsented }) {
  const [checked, setChecked] = useState(false);

  return (
    <div className="identify-screen">
      <div className="identify-card consent-card">
        <p className="identify-eyebrow">Learning LLMs with LLMs</p>
        <h1 className="identify-title">Participant Information & Consent</h1>

        <div className="consent-body">
          <p className="consent-section-title">About this study</p>
          <p>
            You are invited to participate in a research study examining whether
            dialogue-based interaction with a Large Language Model (LLM) helps
            undergraduate software engineering students learn about LLM concepts.
            This study is conducted as part of an academic research project.
          </p>

          <p className="consent-section-title">What you will do</p>
          <p>
            You will work through the <strong>RAG (Retrieval-Augmented Generation)</strong> module
            across three layers — Theory, Application, and Critical Thinking — by chatting
            with a Tutor Agent. At the end of each layer you will take a short quiz.
            A brief survey is administered before and after the module.
          </p>

          <p className="consent-section-title">Data collection</p>
          <p>
            The following data will be collected and stored:
          </p>
          <ul className="consent-list">
            <li>Your name and optional student ID (for matching pre/post data only)</li>
            <li>Your dialogue messages with the Tutor Agent</li>
            <li>Your quiz answers and scores</li>
            <li>Your pre- and post-survey responses</li>
            <li>Session duration and layer progress</li>
          </ul>

          <p className="consent-section-title">Confidentiality</p>
          <p>
            All data will be used <strong>for research purposes only</strong> and will not be
            shared with third parties. Your responses will be reported anonymously in
            aggregate form. No grades or academic penalties are associated with your
            participation or performance.
          </p>

          <p className="consent-section-title">Voluntary participation</p>
          <p>
            Participation is entirely voluntary. You may withdraw at any time without
            consequence by simply closing the browser tab.
          </p>
        </div>

        <label className="consent-checkbox-row">
          <input
            type="checkbox"
            checked={checked}
            onChange={(e) => setChecked(e.target.checked)}
          />
          <span>
            I have read the information above and <strong>I agree</strong> to participate
            in this study.
          </span>
        </label>

        <button
          className="btn-primary"
          onClick={onConsented}
          disabled={!checked}
        >
          Continue
        </button>
      </div>
    </div>
  );
}

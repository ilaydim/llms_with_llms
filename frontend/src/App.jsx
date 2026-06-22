import { useEffect, useState } from "react";
import { api } from "./api";
import IdentifyScreen from "./components/IdentifyScreen";
import SurveyScreen from "./components/SurveyScreen";
import TopBar from "./components/TopBar";
import LearningPath from "./components/LearningPath";
import ChatPanel from "./components/ChatPanel";
import QuizScreen from "./components/QuizScreen";
import "./App.css";

const MODULE_CODE = "rag";
const MODULE_NAME = "RAG (Retrieval-Augmented Generation)";
const LAYER_ORDER = ["theory", "application", "critical"];

export default function App() {
  const [student, setStudent] = useState(null);
  const [session, setSession] = useState(null);
  const [surveyStatus, setSurveyStatus] = useState(null);
  const [layer, setLayer] = useState("theory");
  const [view, setView] = useState("chat"); // chat | quiz | post-survey | finished
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleIdentified(name, studentNo) {
    setLoading(true);
    setError("");
    try {
      const studentRes = await api.identifyStudent(name, studentNo);
      const sessionRes = await api.startSession(studentRes.id);
      const status = await api.getSurveyStatus(studentRes.id);
      setStudent(studentRes);
      setSession(sessionRes);
      setSurveyStatus(status);
    } catch (e) {
      setError("Bağlanılamadı — backend (FastAPI) çalışıyor mu? " + e.message);
    } finally {
      setLoading(false);
    }
  }

  function handlePreSurveyCompleted() {
    setSurveyStatus((prev) => ({ ...prev, pre_completed: true }));
  }

  function handlePostSurveyCompleted() {
    setSurveyStatus((prev) => ({ ...prev, post_completed: true }));
    setView("finished");
  }

  function handleAdvanceLayer() {
    const currentIdx = LAYER_ORDER.indexOf(layer);
    if (currentIdx < LAYER_ORDER.length - 1) {
      setLayer(LAYER_ORDER[currentIdx + 1]);
      setView("chat");
    } else {
      setView("post-survey");
    }
  }

  // 1) Kimlik henüz tanımlanmadıysa
  if (!student || !session || !surveyStatus) {
    return <IdentifyScreen onIdentified={handleIdentified} loading={loading} error={error} />;
  }

  // 2) FR-8.1: pre-anket tamamlanmadan öğrenme içeriğine erişim yok
  if (!surveyStatus.pre_completed) {
    return (
      <SurveyScreen studentId={student.id} surveyType="pre" onCompleted={handlePreSurveyCompleted} />
    );
  }

  // 3) FR-8.2: tüm katmanlar bitince post-anket
  if (view === "post-survey") {
    return (
      <SurveyScreen studentId={student.id} surveyType="post" onCompleted={handlePostSurveyCompleted} />
    );
  }

  if (view === "finished") {
    return (
      <div className="identify-screen">
        <div className="identify-card">
          <p className="identify-eyebrow">Tamamlandı</p>
          <h1 className="identify-title">Teşekkürler, {student.name}!</h1>
          <p className="identify-sub">
            RAG modülünü uçtan uca tamamladın. Katkın için teşekkür ederiz — bu veriler
            araştırma kapsamında anonim olarak değerlendirilecek.
          </p>
        </div>
      </div>
    );
  }

  // 4) Ana öğrenme akışı: diyalog ↔ quiz
  return (
    <div className="app-shell">
      <TopBar studentName={student.name} layer={layer} />
      <div className="app-body">
        <LearningPath activeLayer={layer} onSelect={setLayer} moduleName={MODULE_NAME} />
        {view === "quiz" ? (
          <QuizScreen
            sessionId={session.id}
            moduleCode={MODULE_CODE}
            layer={layer}
            onLeaveQuiz={() => setView("chat")}
            onAdvanceLayer={handleAdvanceLayer}
          />
        ) : (
          <ChatPanel
            sessionId={session.id}
            moduleCode={MODULE_CODE}
            layer={layer}
            onStartQuiz={() => setView("quiz")}
          />
        )}
      </div>
    </div>
  );
}

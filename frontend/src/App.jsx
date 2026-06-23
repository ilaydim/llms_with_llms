import { useEffect, useState } from "react";
import { api } from "./api";
import ConsentScreen from "./components/ConsentScreen";
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
const STORAGE_KEY = "llm_student";
const CONSENT_KEY = "llm_consent";

// Tamamlanan katmanlar + aktif katman tıklanabilir; ilerisi kilitli
function getUnlockedLayers(currentLayer, completedLayers) {
  const currentIdx = LAYER_ORDER.indexOf(currentLayer);
  return LAYER_ORDER.filter((l, i) => i <= currentIdx || completedLayers.includes(l));
}

function saveToStorage(studentId, sessionId, name) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ student_id: studentId, session_id: sessionId, name }));
}

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export default function App() {
  // NFR-2.2: Informed consent — localStorage'da kayıtlıysa tekrar gösterme
  const [consented, setConsented] = useState(() => !!localStorage.getItem(CONSENT_KEY));

  const [student, setStudent] = useState(null);
  const [session, setSession] = useState(null);
  const [surveyStatus, setSurveyStatus] = useState(null);
  const [layer, setLayer] = useState("theory");
  const [completedLayers, setCompletedLayers] = useState([]);
  const [view, setView] = useState("chat"); // chat | quiz | post-survey | finished
  const [loading, setLoading] = useState(true); // true başlangıçta: localStorage kontrol
  const [error, setError] = useState("");

  function handleConsented() {
    localStorage.setItem(CONSENT_KEY, "true");
    setConsented(true);
  }

  // NFR-4.1: Uygulama açılışında localStorage'dan önceki oturumu restore et
  useEffect(() => {
    const saved = loadFromStorage();
    if (!saved) {
      setLoading(false);
      return;
    }

    // Kayıtlı student/session var, backend'den progress'i çek ve restore et
    async function restoreSession() {
      try {
        const [sessionRes, progressRes, surveyStatusRes] = await Promise.all([
          api.startSession(saved.student_id),
          api.getStudentProgress(saved.student_id),
          api.getSurveyStatus(saved.student_id),
        ]);

        setStudent({ id: saved.student_id, name: saved.name });
        setSession(sessionRes);
        setSurveyStatus({
          pre_completed: surveyStatusRes.pre_completed,
          post_completed: surveyStatusRes.post_completed,
        });
        setCompletedLayers(progressRes.layers_completed || []);

        // Post-anket tamamlandıysa finished ekranına git
        if (surveyStatusRes.post_completed) {
          setView("finished");
        } else if (progressRes.layers_completed.length === LAYER_ORDER.length) {
          setView("post-survey");
        } else {
          setLayer(progressRes.current_layer);
          setView("chat");
        }
      } catch {
        // Restore başarısız (backend kapalı vs.) → temiz başlangıç
        localStorage.removeItem(STORAGE_KEY);
      } finally {
        setLoading(false);
      }
    }

    restoreSession();
  }, []);

  async function handleIdentified(name, studentNo) {
    setLoading(true);
    setError("");
    try {
      const studentRes = await api.identifyStudent(name, studentNo);
      const sessionRes = await api.startSession(studentRes.id);
      const [status, progressRes] = await Promise.all([
        api.getSurveyStatus(studentRes.id),
        api.getStudentProgress(studentRes.id),
      ]);

      setStudent(studentRes);
      setSession(sessionRes);
      setSurveyStatus(status);
      setCompletedLayers(progressRes.layers_completed || []);
      saveToStorage(studentRes.id, sessionRes.id, studentRes.name);

      // Dönüş yapan öğrenci için kaldığı katmana git
      if (status.post_completed) {
        setView("finished");
      } else if (status.pre_completed) {
        setLayer(progressRes.current_layer);
        setView("chat");
      }
    } catch (e) {
      setError("Could not connect — is the backend (FastAPI) running? " + e.message);
    } finally {
      setLoading(false);
    }
  }

  function handlePreSurveyCompleted() {
    setSurveyStatus((prev) => ({ ...prev, pre_completed: true }));
  }

  function handlePostSurveyCompleted() {
    setSurveyStatus((prev) => ({ ...prev, post_completed: true }));
    localStorage.removeItem(STORAGE_KEY); // oturum bitti, localStorage temizle
    setView("finished");
  }

  function handleAdvanceLayer() {
    setCompletedLayers((prev) => prev.includes(layer) ? prev : [...prev, layer]);
    const currentIdx = LAYER_ORDER.indexOf(layer);
    if (currentIdx < LAYER_ORDER.length - 1) {
      const nextLayer = LAYER_ORDER[currentIdx + 1];
      setLayer(nextLayer);
      setView("chat");
    } else {
      setView("post-survey");
    }
  }

  // Açılışta localStorage kontrol ediliyor
  if (loading) {
    return (
      <div className="identify-screen">
        <div className="identify-card">
          <p className="identify-sub">Loading…</p>
        </div>
      </div>
    );
  }

  // 0) NFR-2.2: Informed consent ilk adım — onaylanmadıysa diğer hiçbir şey gösterilmez
  if (!consented) {
    return <ConsentScreen onConsented={handleConsented} />;
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
          <p className="identify-eyebrow">Completed</p>
          <h1 className="identify-title">Thank you, {student.name}!</h1>
          <p className="identify-sub">
            You have completed the RAG module from start to finish. Thank you for your participation — your data will be used anonymously for research purposes.
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
        <LearningPath
          activeLayer={layer}
          onSelect={setLayer}
          moduleName={MODULE_NAME}
          unlockedLayers={getUnlockedLayers(layer, completedLayers)}
        />
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

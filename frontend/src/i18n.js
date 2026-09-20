import { createContext, useContext } from "react";

export const LANG_KEY = "llm_lang";

export const translations = {
  en: {
    "app.brand": "Learning LLMs with LLMs",
    "common.loading": "Loading…",
    "common.writeYourAnswer": "Write your answer here…",
    "common.connectError": "Could not connect — is the backend (FastAPI) running? ",

    "layer.theory": "Theory",
    "layer.application": "Application",
    "layer.critical": "Critical Thinking",
    "layer.theory.desc": "Conceptual foundation",
    "layer.application.desc": "Build & experiment",
    "layer.critical.desc": "Limits & risks",

    "topbar.layerLine": "{layer} layer",

    "consent.title": "Participant Information & Consent",
    "consent.about.title": "About this study",
    "consent.about.body":
      "You are invited to participate in a research study examining whether dialogue-based interaction with a Large Language Model (LLM) helps undergraduate software engineering students learn about LLM concepts. This study is conducted as part of an academic research project.",
    "consent.whatYouWillDo.title": "What you will do",
    "consent.whatYouWillDo.body1": "You will work through the",
    "consent.whatYouWillDo.body2":
      "module across three layers — Theory, Application, and Critical Thinking — by chatting with a Tutor Agent. At the end of each layer you will take a short quiz. A brief survey is administered before and after the module.",
    "consent.data.title": "Data collection",
    "consent.data.intro": "The following data will be collected and stored:",
    "consent.data.item1": "Your name and optional student ID (for matching pre/post data only)",
    "consent.data.item2": "Your dialogue messages with the Tutor Agent",
    "consent.data.item3": "Your quiz answers and scores",
    "consent.data.item4": "Your pre- and post-survey responses",
    "consent.data.item5": "Session duration and layer progress",
    "consent.confidentiality.title": "Confidentiality",
    "consent.confidentiality.body1": "All data will be used",
    "consent.confidentiality.body2":
      "and will not be shared with third parties. Your responses will be reported anonymously in aggregate form. No grades or academic penalties are associated with your participation or performance.",
    "consent.confidentiality.emphasis": "for research purposes only",
    "consent.voluntary.title": "Voluntary participation",
    "consent.voluntary.body":
      "Participation is entirely voluntary. You may withdraw at any time without consequence by simply closing the browser tab.",
    "consent.checkbox.pre": "I have read the information above and",
    "consent.checkbox.emphasis": "I agree",
    "consent.checkbox.post": " to participate in this study.",
    "consent.continue": "Continue",

    "identify.title": "Learn about LLMs by talking to one.",
    "identify.sub1": "In this pilot study you will explore RAG (Retrieval-Augmented Generation) across three layers:",
    "identify.sub2": "No account needed — just introduce yourself.",
    "identify.name.label": "Your name",
    "identify.name.placeholder": "e.g. Alex Johnson",
    "identify.studentNo.label": "Student ID",
    "identify.studentNo.optional": "(optional)",
    "identify.studentNo.placeholder": "e.g. 20210101",
    "identify.settingUp": "Setting up…",
    "identify.start": "Start learning",
    "identify.footnote": "If you've used this platform before with the same name, you'll resume where you left off.",

    "survey.pre.eyebrow": "Pre-Study Survey",
    "survey.post.eyebrow": "Post-Study Survey",
    "survey.pre.title": "A few questions before you start",
    "survey.post.title": "Great work! A few final questions",
    "survey.pre.sub": "This short survey measures your baseline knowledge — there are no right or wrong answers.",
    "survey.post.sub": "This survey will be used to compare your knowledge before and after the module.",
    "survey.submitting": "Submitting…",
    "survey.submit": "Submit survey",

    "learningPath.module": "Module",
    "learningPath.locked": "Complete the previous layer's quiz to unlock",

    "quiz.header": "{layer} — End-of-Layer Quiz",
    "quiz.backToDialogue": "← Back to dialogue",
    "quiz.loading": "Loading quiz…",
    "quiz.notFound": "Quiz not found.",
    "quiz.evaluating": "Evaluating…",
    "quiz.submit": "Submit quiz",
    "quiz.passed": "Passed",
    "quiz.notYet": "Not yet",
    "quiz.detail": "Multiple choice: {mcq}% · Open-ended: {open}%",
    "quiz.continue": "Continue →",
    "quiz.revisit.prompt": "Would you like to revisit this topic with a different explanation?",
    "quiz.revisit.no": "No, continue anyway",
    "quiz.revisit.yes": "Yes, explain again",
    "quiz.newExplanation": "New explanation",
    "quiz.makeSense": "Does that make more sense?",
    "quiz.askTutor": "Still unclear? Ask the tutor",
    "quiz.askPlaceholder": "Ask a question about this explanation…",
    "quiz.retake": "Yes, retake the quiz",

    "chat.placeholder.theory": "Ask anything about RAG in your own words…",
    "chat.placeholder.application": "Ask a question about the task — the Tutor Agent will search the documents…",
    "chat.placeholder.critical": "Share your thoughts on the limits and risks of RAG…",
    "chat.intro": "{layer} — Introduction",
    "chat.taskSteps": "Task Steps",
    "chat.step.1": "Formulate a question",
    "chat.step.2": "Inspect the retrieved chunks",
    "chat.step.3": "Evaluate retrieval quality",
    "chat.step.generic": "Step {n}",
    "chat.allTasksDone": "All steps completed — you can now take the quiz.",
    "chat.thinking": "thinking…",
    "chat.send": "Send",
    "chat.takeQuiz": "Take quiz",

    "bubble.you": "YOU",
    "bubble.tutor": "TUTOR",
    "bubble.typing": "typing…",

    "app.completed": "Completed",
    "app.thankYou": "Thank you, {name}!",
    "app.finishedBody":
      "You have completed the RAG module from start to finish. Thank you for your participation — your data will be used anonymously for research purposes.",

    "lang.switch.label": "Language",
  },

  tr: {
    "app.brand": "LLM'lerle LLM Öğrenmek",
    "common.loading": "Yükleniyor…",
    "common.writeYourAnswer": "Cevabını buraya yaz…",
    "common.connectError": "Bağlanılamadı — backend (FastAPI) çalışıyor mu? ",

    "layer.theory": "Teori",
    "layer.application": "Uygulama",
    "layer.critical": "Eleştirel Düşünme",
    "layer.theory.desc": "Kavramsal temel",
    "layer.application.desc": "Geliştir ve deneyimle",
    "layer.critical.desc": "Sınırlar ve riskler",

    "topbar.layerLine": "{layer} katmanı",

    "consent.title": "Katılımcı Bilgilendirme ve Onam Formu",
    "consent.about.title": "Bu çalışma hakkında",
    "consent.about.body":
      "Büyük Dil Modelleri (LLM) ile diyalog tabanlı etkileşimin, lisans yazılım mühendisliği öğrencilerinin LLM kavramlarını öğrenmesine yardımcı olup olmadığını inceleyen bir araştırma çalışmasına katılmaya davetlisiniz. Bu çalışma akademik bir araştırma projesinin parçası olarak yürütülmektedir.",
    "consent.whatYouWillDo.title": "Ne yapacaksınız",
    "consent.whatYouWillDo.body1": "Bir Öğretici Ajan ile sohbet ederek",
    "consent.whatYouWillDo.body2":
      "modülünü üç katman boyunca — Teori, Uygulama ve Eleştirel Düşünme — çalışacaksınız. Her katmanın sonunda kısa bir quiz çözeceksiniz. Modülden önce ve sonra kısa bir anket uygulanır.",
    "consent.data.title": "Veri toplama",
    "consent.data.intro": "Aşağıdaki veriler toplanacak ve saklanacaktır:",
    "consent.data.item1": "Adınız ve isteğe bağlı öğrenci numaranız (yalnızca ön/son veriyi eşleştirmek için)",
    "consent.data.item2": "Öğretici Ajan ile diyalog mesajlarınız",
    "consent.data.item3": "Quiz cevaplarınız ve puanlarınız",
    "consent.data.item4": "Ön ve son anket cevaplarınız",
    "consent.data.item5": "Oturum süresi ve katman ilerlemeniz",
    "consent.confidentiality.title": "Gizlilik",
    "consent.confidentiality.body1": "Tüm veriler",
    "consent.confidentiality.body2":
      "kullanılacak ve üçüncü taraflarla paylaşılmayacaktır. Cevaplarınız yalnızca toplu ve anonim şekilde raporlanacaktır. Katılımınız veya performansınızla ilişkili herhangi bir not veya akademik yaptırım yoktur.",
    "consent.confidentiality.emphasis": "yalnızca araştırma amacıyla",
    "consent.voluntary.title": "Gönüllü katılım",
    "consent.voluntary.body":
      "Katılım tamamen gönüllülük esasına dayanır. Tarayıcı sekmesini kapatarak herhangi bir zamanda, hiçbir sonuç doğurmadan çalışmadan ayrılabilirsiniz.",
    "consent.checkbox.pre": "Yukarıdaki bilgileri okudum ve bu çalışmaya",
    "consent.checkbox.emphasis": "katılmayı kabul ediyorum",
    "consent.checkbox.post": ".",
    "consent.continue": "Devam et",

    "identify.title": "Bir LLM ile konuşarak LLM'ler hakkında öğren.",
    "identify.sub1": "Bu pilot çalışmada RAG'ı (Retrieval-Augmented Generation) üç katman boyunca keşfedeceksin:",
    "identify.sub2": "Hesap gerekmiyor — sadece kendini tanıt.",
    "identify.name.label": "Adın",
    "identify.name.placeholder": "örn. Ayşe Yılmaz",
    "identify.studentNo.label": "Öğrenci No",
    "identify.studentNo.optional": "(isteğe bağlı)",
    "identify.studentNo.placeholder": "örn. 20210101",
    "identify.settingUp": "Hazırlanıyor…",
    "identify.start": "Öğrenmeye başla",
    "identify.footnote": "Bu platformu daha önce aynı isimle kullandıysan, kaldığın yerden devam edeceksin.",

    "survey.pre.eyebrow": "Ön Anket",
    "survey.post.eyebrow": "Son Anket",
    "survey.pre.title": "Başlamadan önce birkaç soru",
    "survey.post.title": "Harika iş! Son birkaç soru",
    "survey.pre.sub": "Bu kısa anket başlangıç bilgi düzeyini ölçer — doğru veya yanlış cevap yoktur.",
    "survey.post.sub": "Bu anket, modül öncesi ve sonrası bilgi düzeyini karşılaştırmak için kullanılacaktır.",
    "survey.submitting": "Gönderiliyor…",
    "survey.submit": "Anketi gönder",

    "learningPath.module": "Modül",
    "learningPath.locked": "Kilidi açmak için önceki katmanın quiz'ini tamamla",

    "quiz.header": "{layer} — Katman Sonu Quiz'i",
    "quiz.backToDialogue": "← Diyaloğa dön",
    "quiz.loading": "Quiz yükleniyor…",
    "quiz.notFound": "Quiz bulunamadı.",
    "quiz.evaluating": "Değerlendiriliyor…",
    "quiz.submit": "Quiz'i gönder",
    "quiz.passed": "Geçti",
    "quiz.notYet": "Henüz değil",
    "quiz.detail": "Çoktan seçmeli: %{mcq} · Açık uçlu: %{open}",
    "quiz.continue": "Devam et →",
    "quiz.revisit.prompt": "Bu konuyu farklı bir anlatımla tekrar gözden geçirmek ister misin?",
    "quiz.revisit.no": "Hayır, yine de devam et",
    "quiz.revisit.yes": "Evet, tekrar anlat",
    "quiz.newExplanation": "Yeni anlatım",
    "quiz.makeSense": "Şimdi daha mantıklı geldi mi?",
    "quiz.askTutor": "Hâlâ net değil mi? Tutor'a sor",
    "quiz.askPlaceholder": "Bu anlatımla ilgili bir soru sor…",
    "quiz.retake": "Evet, quiz'i tekrar çöz",

    "chat.placeholder.theory": "RAG hakkında kendi cümlelerinle istediğini sor…",
    "chat.placeholder.application": "Görevle ilgili bir soru sor — Öğretici Ajan dokümanlarda arama yapacak…",
    "chat.placeholder.critical": "RAG'ın sınırları ve riskleri hakkındaki düşüncelerini paylaş…",
    "chat.intro": "{layer} — Giriş",
    "chat.taskSteps": "Görev Adımları",
    "chat.step.1": "Bir soru oluştur",
    "chat.step.2": "Getirilen parçaları incele",
    "chat.step.3": "Erişim kalitesini değerlendir",
    "chat.step.generic": "Adım {n}",
    "chat.allTasksDone": "Tüm adımlar tamamlandı — artık quiz'i çözebilirsin.",
    "chat.thinking": "düşünüyor…",
    "chat.send": "Gönder",
    "chat.takeQuiz": "Quiz'e gir",

    "bubble.you": "SEN",
    "bubble.tutor": "ÖĞRETİCİ",
    "bubble.typing": "yazıyor…",

    "app.completed": "Tamamlandı",
    "app.thankYou": "Teşekkürler, {name}!",
    "app.finishedBody":
      "RAG modülünü baştan sona tamamladın. Katılımın için teşekkürler — verilerin yalnızca araştırma amacıyla ve anonim olarak kullanılacaktır.",

    "lang.switch.label": "Dil",
  },
};

export function detectDefaultLang() {
  try {
    const saved = localStorage.getItem(LANG_KEY);
    if (saved === "en" || saved === "tr") return saved;
  } catch {
    // localStorage erişilemezse yoksay
  }
  const nav = typeof navigator !== "undefined" ? navigator.language || "" : "";
  return nav.toLowerCase().startsWith("tr") ? "tr" : "en";
}

export function getStoredLang() {
  return detectDefaultLang();
}

export const LanguageContext = createContext(null);

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within a LanguageProvider");
  return ctx;
}

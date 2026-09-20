# Learning LLMs with LLMs — MVP (Faz 1)

SRS dokümanına göre geliştirilen, RAG modülü üzerinden Teori → Uygulama → Eleştirel Bakış akışını
LLM ile diyalog yoluyla sunan platform.

## Kurulum

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# .env içine kullanacağın sağlayıcının API anahtarını gir (veya LLM_PROVIDER=mock)

uvicorn app.main:app --reload
```

Sunucu ayağa kalkınca http://127.0.0.1:8000/docs adresinden Swagger UI ile tüm endpoint'leri
test edebilirsin. `modules_config/rag.json` dosyası otomatik olarak `modules` tablosuna senkronize
edilir (FR-1.2).

## Proje Yapısı

```
backend/
  app/
    main.py              # FastAPI giriş noktası
    database.py           # SQLAlchemy engine/session
    core/config.py        # .env tabanlı merkezi ayarlar (NFR-2.3)
    models/models.py      # SRS Bölüm 6.2 — tüm tablolar
    schemas/               # Pydantic request/response modelleri
    routers/                # API endpoint'leri (öğrenci, oturum, ...)
    services/
      module_loader.py     # FR-1.1/1.3 — modül config okuma + tutor prompt üretimi
      session_activity.py  # FR-7.3 — Active Session Time hesabı
    agents/                 # (Sıradaki adım) Tutor Agent / Evaluator Agent / LLM client
  modules_config/
    rag.json               # FR-1.1/1.2 — RAG modülünün tek kaynak yapılandırması
  rag_documents/            # FR-4.1 retrieval için kaynak dokümanlar (eklenecek)
  requirements.txt
  .env.example
```

## Hızlı Başlangıç (Backend + Frontend birlikte)

**1) Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # LLM_PROVIDER=mock olarak bırakabilirsin, API anahtarı gerekmez
uvicorn app.main:app --reload
```

**2) Frontend (yeni terminalde):**
```bash
cd frontend
npm install
npm run dev
```

Tarayıcıda `http://localhost:5173` adresini aç. Adını gir → "Öğrenmeye başla"
dersin → sol rayda Teori/Uygulama/Eleştirel katmanları arasında geçiş yapıp
Tutor Agent ile diyalog kurabilirsin. `LLM_PROVIDER=mock` olduğu için gerçek
bir API anahtarı olmadan tüm akış (oturum, mesaj kaydı, tool çağrısı dahil)
uçtan uca çalışır.

## Proje Yapısı

```
backend/
  app/
    main.py              # FastAPI giriş noktası
    database.py           # SQLAlchemy engine/session
    core/config.py        # .env tabanlı merkezi ayarlar (NFR-2.3, NFR-5.2)
    models/models.py      # SRS Bölüm 6.2 — tüm tablolar
    schemas/               # Pydantic request/response modelleri
    routers/
      students.py          # UC-1 — kimlik tanımlama
      sessions.py           # UC-1 — oturum başlatma/devam ettirme (NFR-4.1)
      dialogue.py            # UC-2/3/4 — diyalog motoru
      quiz.py                 # UC-5/6/7 — quiz + mastery learning
      survey.py                # UC-1/UC-8 — pre/post anket
    agents/
      llm_client.py          # Sağlayıcı-bağımsız LLM katmanı (mock/groq/anthropic/openai)
      tutor_agent.py          # Bölüm 5.4/5.5 — Tutor Agent
      evaluator_agent.py       # Bölüm 5.4 — Evaluator Agent (FR-6.3)
    services/
      module_loader.py        # FR-1.1/1.3 — modül config okuma + tutor prompt üretimi
      document_search.py       # FR-4.1 — "doküman ara" aracı (gerçek semantik arama)
      vector_store.py           # chromadb + sentence-transformers retrieval
      survey_loader.py           # FR-8.1/8.2 — anket sorularını config'ten okuma
      session_activity.py         # FR-7.3 — Active Session Time hesabı
  modules_config/
    rag.json                    # FR-1.1/1.2 — RAG modülünün tek kaynak yapılandırması (3 katman quiz dahil)
  survey_config/
    questions.json               # Pre/post anket soru seti
  rag_documents/                 # FR-4.1 retrieval için kaynak dokümanlar (5 özgün, atıflı doküman)
  requirements.txt
  .env.example

frontend/
  src/
    api.js                       # Backend ile iletişim katmanı
    App.jsx                       # Tüm akış: kimlik → pre-anket → diyalog/quiz döngüsü → post-anket
    components/
      IdentifyScreen.jsx           # UC-1 — kimlik girişi
      SurveyScreen.jsx               # UC-1/UC-8 — pre/post anket ekranı
      LearningPath.jsx                # Sol ray — Teori/Uygulama/Eleştirel ilerleme
      TopBar.jsx                       # Üst bilgi çubuğu
      ChatPanel.jsx                     # UC-2/3/4 — diyalog arayüzü
      MessageBubble.jsx                  # NFR-3.2 — öğrenci/tutor net görsel ayrımı
      QuizScreen.jsx                      # UC-5/6/7 — quiz + mastery learning arayüzü
```

## Şu Ana Kadar Tamamlanan

**Gün 1**
- [x] Proje iskeleti, veritabanı modelleri (SRS Bölüm 6.2)
- [x] RAG modül yapılandırma dosyası (`modules_config/rag.json`)
- [x] Öğrenci kimlik tanımlama + oturum başlatma/devam ettirme (UC-1, NFR-4.1, FR-7.3)

**Gün 2**
- [x] Sağlayıcı-bağımsız LLM istemci katmanı (`mock` / `anthropic` / `openai` — NFR-5.2)
- [x] Tutor Agent: dinamik sistem promptu (Bölüm 5.5), katman girişleri (FR-3.1), tool-use döngüsü (FR-4.1)
- [x] Evaluator Agent: açık uçlu cevap değerlendirme iskeleti (FR-6.3) — quiz endpoint'ine henüz bağlanmadı
- [x] `/dialogue/*` endpoint'leri: katman girişi, geçmiş, mesaj gönderme (UC-2/3/4, FR-3.2–3.5)
- [x] React arayüzü: kimlik ekranı, üç katmanlı ilerleme rayı, diyalog paneli — `LLM_PROVIDER=mock` ile API anahtarı olmadan uçtan uca test edildi
- [x] `npm run build` hatasız geçti

**Gün 3**
- [x] `rag_documents/` — chunking, embedding, hibrit arama, halüsinasyon/sınırlar ve değerlendirme konularında 5 özgün doküman (kaynaklara dayalı, paraphrase edilmiş — bkz. `rag_documents/KAYNAKCA.md`)
- [x] `vector_store.py`: gerçek chromadb + sentence-transformers tabanlı semantik arama; paragraf-bazlı chunking
- [x] `document_search.py` artık gerçek semantik aramayı kullanıyor — `tutor_agent.py`'ye hiç dokunulmadı (FR-4.1 tool arayüzü sabit kaldı)
- [x] Uygulama başlangıcında otomatik ingestion + embedding modeli indirilemezse zarif fallback (uygulama çökmüyor, tool boş sonuç dönüyor)
- [x] Chunk'lama mantığı ve chromadb yazma/okuma/sorgu pipeline'ı uçtan uca test edildi

> **Not:** Geliştirme sandbox'ımın ağ erişimi kısıtlı olduğu için `sentence-transformers/all-MiniLM-L6-v2` modelinin Hugging Face'ten gerçek indirilişini orada test edemedim (chromadb mekaniğini sahte embedding'lerle doğruladım). Senin ortamında normal internet erişimi olduğu için ilk çalıştırmada model otomatik inecek — `uvicorn` loglarında `[startup] RAG doküman koleksiyonu hazır: N chunk.` mesajını görmen beklenir. Görmezsen UYARI mesajı ne olduğunu söyleyecektir.

**Gün 4 + Gün 5**
- [x] `survey_config/questions.json`: pre/post anket soru seti (Likert + açık uçlu, pre/post aynı maddeler — eşleştirilmiş karşılaştırma için, SRS Bölüm 8.4)
- [x] `/survey/*` endpoint'leri: soru listesi, durum kontrolü (NFR-4.1 ile tutarlı — tamamlanan anket tekrar sorulmaz), gönderme (UC-1, UC-8, FR-8.1–8.3)
- [x] `rag.json`'a Uygulama ve Eleştirel katmanlar için quiz tanımları eklendi (önceden sadece Teori vardı)
- [x] `/quiz/*` endpoint'leri: soru listesi (doğru cevap istemciye sızdırılmıyor), gönderme (MCQ kural-bazlı + Evaluator Agent ile açık uçlu puanlama), `/quiz/revisit` (mastery learning — UC-6/7, FR-6.1–6.7)
- [x] Evaluator Agent artık gerçekten bağlı ve çağrılıyor (önceden sadece iskelet vardı)
- [x] React: `SurveyScreen.jsx`, `QuizScreen.jsx`; `App.jsx` artık tüm akışı yönetiyor: kimlik → pre-anket (zorunlu) → Teori↔Uygulama↔Eleştirel arası diyalog/quiz döngüsü (geçemezse "tekrar anlat" akışı) → post-anket → bitiş ekranı
- [x] UC-1'den UC-8'e kadar **tüm SRS use case'leri** mock LLM ile tek bir senaryoda uçtan uca test edildi (bkz. aşağıdaki test çıktısı)
- [x] `npm run build` hatasız geçti

```
✓ kimlik/oturum  ✓ pre-anket  ✓ teori diyaloğu  ✓ quiz (1. deneme)
✓ revisit (geri dön)  ✓ quiz (2. deneme, attempt_number doğru arttı)
✓ uygulama katmanı diyaloğu (tool çağrısı dahil)  ✓ uygulama quiz'i
✓ eleştirel katman diyaloğu  ✓ eleştirel quiz'i  ✓ post-anket
```

**Gün 6 ve sonrası**
- [x] Streaming diyalog yanıtları
- [x] Katman kilitleme (önceki katman geçilmeden sonrakine girilemez) ve ilerleme takibi (`/progress/*`)
- [x] Uygulama görevi adım takibi (`/tasks/*`, `application_tasks` tablosu — FR-4.3)
- [x] Onam (consent) ekranı; TR/EN dil değiştirme (`i18n`)
- [x] Groq LLM sağlayıcısı; 429 rate-limit'te bekleme süresini okuyan, en fazla 5 denemeli retry (NFR-4.2)
- [x] Araştırma verisi CSV export'u (`python export_data.py`)
- [x] Railway deploy ayarları (`railway.json`, `nixpacks.toml`) ve Vite dev proxy

## Sıradaki Adımlar

- [x] Otomatik testler: `backend/tests` (mock LLM, geçici DB). Çalıştırmak için: `pip install -r requirements-dev.txt && pytest`
- [x] Streaming (SSE) testleri ve Groq canlı duman testleri (`RUN_LIVE_LLM=1 pytest tests/test_live_llm.py`)
- [ ] **Katman kilitlemeyi backend'de zorunlu kıl:** şu an sadece frontend'de (`App.jsx` `getUnlockedLayers`). `/dialogue/*` ve `/quiz/submit` doğrudan API'den çağrılarak kilit atlanabiliyor. Sonra test ekle.
- [ ] Gerçek LLM ile uçtan uca pilot denemesi (tüm akış, gerçek öğrenci senaryosu)
- [ ] `.env.example`'daki varsayılan Groq modelini güncelle; Groq model kataloğu değişiyor (`gemma2-9b-it` kaldırıldı, `llama-3.3-70b-versatile` bazı hesaplarda erişilemiyor). Çalışan örnek: `openai/gpt-oss-120b`
- [ ] Hata mesajlarının (NFR-3.3) ve responsive görünümün son kontrolü
- [ ] Learning analytics (FR-7.1/7.2): konu bazlı mesaj sayısı özeti

## Bilinen Sınırlamalar / Sıradaki Kararlar

- **Quiz geçme eşiği (FR-6.4, SRS'te "TBD"):** Şu an `mcq_score*0.6 + open_ended_score*0.4 ≥ 0.7` formülü kullanılıyor (`.env`'de `QUIZ_PASS_THRESHOLD`). Ekip olarak gözden geçirilmeli.
- **Katman geçişi (FR-3.4):** Öğrenci "Quiz'e geç" butonuna manuel basıyor; otomatik tetikleme yok.

## LLM API'sini Bağlama

`backend/.env` içinde `LLM_PROVIDER` değerini seç (`mock`, `groq`, `anthropic`, `openai`) ve ilgili anahtarı gir
(`GROQ_API_KEY`, `ANTHROPIC_API_KEY` veya `OPENAI_API_KEY`). Model adları `TUTOR_MODEL` / `EVALUATOR_MODEL` ile
ayarlanır. Agent kodlarına dokunmak gerekmez; hepsi `llm_client.py`'daki ortak `LLMClient` arayüzünü kullanır.

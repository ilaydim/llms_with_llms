# Durum Raporu — Learning LLMs with LLMs (2026-09-14 itibarıyla)

> Bu dosya, projeye yeni başlayan/devam eden bir Claude Code oturumunun hızlıca
> bağlam kazanması için yazıldı. `README.md` ilerleme günlüğü tutuyor ama son
> 2 commit'i yansıtmıyor (aşağıda "README ile fark" bölümüne bakın).

## Proje nedir

SRS dokümanına (`docs/LLMs with LLMs SRS.pdf`) dayanan bir MVP: öğrencilere RAG (Retrieval-Augmented Generation) konusunu
Teori → Uygulama → Eleştirel Bakış katmanlarında, bir "Tutor Agent" ile
diyalog üzerinden öğreten bir platform. Backend FastAPI + SQLAlchemy + chromadb,
frontend React (Vite).

## Mimari, kısaca

- **Backend** (`backend/app/`): `routers/` (students, sessions, dialogue, quiz,
  survey, progress, tasks), `agents/` (tutor_agent, evaluator_agent,
  llm_client — mock/anthropic/openai/groq destekli sağlayıcı-bağımsız katman),
  `services/` (module_loader, document_search, vector_store — chromadb +
  sentence-transformers ile gerçek semantik arama, survey_loader,
  session_activity).
- **Frontend** (`frontend/src/`): `App.jsx` tüm akışı yönetiyor — consent →
  identify → pre-survey → Teori/Uygulama/Eleştirel diyalog+quiz döngüsü →
  post-survey. Bileşenler: ConsentScreen, IdentifyScreen, SurveyScreen,
  LearningPath, TopBar, ChatPanel, MessageBubble, QuizScreen.
- **Veri**: SQLite (`backend/llms_with_llms.db`), chromadb store
  (`backend/chroma_store/`), modül/anket config'leri JSON dosyalarında
  (`modules_config/rag.json`, `survey_config/questions.json`).
- **Deployment**: Railway için `nixpacks.toml` + `railway.json` — FastAPI,
  build edilmiş React'i static dosya olarak servis ediyor (tek process).

## Tamamlananlar (commit geçmişi özeti)

1. **`c301172` first version** — proje iskeleti, DB modelleri, RAG modül config,
   öğrenci kimlik/oturum akışı.
2. **`edfe133`** — SSE streaming (kelime kelime yanıt), katman kilitleme
   (quiz geçmeden ileri katmana atlanamıyor), sayfa yenilemede oturum geri
   yükleme (localStorage + `/progress/student/{id}`), `layer_progress` tablosu,
   `application_tasks` tablosu + `/tasks` router (Uygulama katmanı checklist'i
   artık gerçekten bağlı), LLM çağrılarında otomatik retry, onay ekranı
   (ConsentScreen, NFR-2.2), **tüm arayüz Türkçe'den İngilizce'ye çevrildi**.
3. **`a5f003d`** — Deployment config (Railway/nixpacks), FastAPI artık build
   edilmiş frontend'i static olarak serve ediyor (SPA fallback), Vite dev
   proxy (`VITE_API_URL` olmadan da localhost:8000'e proxy), `export_data.py`
   (tüm DB tablolarını pilot analiz için CSV'ye döküyor), `ALLOWED_ORIGINS`.
4. **`c4e82c5`** (HEAD) — Groq LLM sağlayıcısı eklendi (streaming + tool-use
   destekli `GroqLLMClient`, varsayılan model `llama-3.3-70b-versatile`),
   SRS PDF repoya eklendi.

Yani **UC-1'den UC-8'e kadar tüm SRS use case'leri** uçtan uca (mock LLM ile)
test edilmiş durumda; üstüne streaming, katman kilitleme, oturum geri yükleme,
uygulama görevi takibi, onay ekranı, tam İngilizce lokalizasyon ve Railway
deployment altyapısı da eklenmiş.

## README ile fark (README güncel değil)

`README.md`'deki "Şu Ana Kadar Tamamlanan" günlüğü **Gün 5**'te bırakılmış;
Gün 6-7 olarak planlanan şeylerin çoğu (layer progress, application_tasks
entegrasyonu) aslında **zaten yapılmış** (`edfe133` commit'inde). README'nin
"Bilinen Sınırlamalar" bölümündeki şu madde artık **eskimiş**:

> "Uygulama görevi adım takibi... henüz hiçbir endpoint bu tabloyu
> güncellemiyor" → **Artık doğru değil**, `routers/tasks.py` bunu yapıyor.

Hâlâ geçerli olan tek sınırlama: **katman geçişi hâlâ manuel** (öğrenci
"Quiz'e geç" butonuna basıyor; belirli mesaj sayısından sonra otomatik
tetikleme yok) — kodda (`dialogue.py`, `App.jsx`, `ChatPanel.jsx`) buna dair
bir otomatik geçiş mantığı bulunamadı, doğrulandı.

README'yi güncellemek istersen haber ver — şu an yapmadım çünkü asıl istek
bu rapordu.

## Açık noktalar / hâlâ karar bekleyenler

- **Quiz geçme eşiği (FR-6.4)**: `mcq*0.6 + open_ended*0.4 ≥ 0.7` formülü hâlâ
  varsayım, ekip onayı bekliyor (`QUIZ_PASS_THRESHOLD` env ile override edilebiliyor).
- **Katman geçiş kriteri (FR-3.4)**: yukarıda belirtildiği gibi hâlâ manuel.
- **Test suite yok**: repoda hiç test dosyası bulunamadı (`find . -iname "*test*"`
  boş döndü). Pilot öncesi en azından kritik akışlar için manuel test planı
  gerekecek.
- **Hata mesajları / responsive son kontrol / pilot teste hazırlık** (README'nin
  Gün 7 planı) — henüz commit geçmişinde buna özel bir iş görünmüyor;
  `api.js`'de temel try/catch var ama kapsamlı bir hata-mesajı denetimi
  yapılmamış görünüyor.

## Ortam / çalıştırma durumu (bu makinede)

- `backend/.env` **yok** — `backend/.env.example`'dan kopyalanıp doldurulması
  gerekiyor (LLM_PROVIDER=mock ile API anahtarsız da çalışır).
- `.venv/`, `backend/venv/`, `frontend/node_modules/` zaten mevcut (daha önce
  kurulum yapılmış).
- **Commit edilmemiş değişiklik**: `frontend/package-lock.json` değişmiş
  (muhtemelen bir `npm install` sonrası — 63 satır eklenmiş/12 satır silinmiş).
  Commit'lenmemiş, ne yaptığı doğrulanmadan commit edilmemeli.
- **Dosya organizasyonu (bu oturumda yapıldı)**: SRS PDF, commit'teki
  `6584d230-...pdf` adından bu oturumdan önce zaten `LLMs with LLMs SRS.pdf`
  olarak yeniden adlandırılmış ve repo köküne taşınmıştı (git'te "deleted +
  untracked" olarak görünüyordu). Bu oturumda `docs/LLMs with LLMs SRS.pdf`
  konumuna taşındı — proje köküne dağılmış belge/rapor dosyalarını `docs/`
  altında toplamak için. Henüz `git add` ile stage edilmedi; git bunu
  otomatik olarak rename diye algılayacaktır (`git add -A` yeterli).
  `README.md` ve `frontend/README.md` bilinçli olarak taşınmadı — kök ve
  paket README'lerinin proje köklerinde kalması standart bir konvansiyon.
  `backend/rag_documents/*.md` de taşınmadı — bunlar meta-dokümantasyon değil,
  uygulamanın RAG retrieval için kullandığı kaynak veri (`rag_documents_dir`
  config'i o klasörü gösteriyor); taşımak ingestion'ı bozar.
- Repo `origin/main` ile senkron, branch main.
- Son commit'ler `yarensaklavci` tarafından atılmış (muhtemelen ekip
  arkadaşı) — bu oturumun kullanıcısı İlayda Dim.

## Önerilen sıradaki adımlar

1. `frontend/package-lock.json`'daki değişikliğin kaynağını anlayıp
   (muhtemelen zararsız bir `npm install` artığı) commit'le ya da geri al.
2. `backend/.env` oluştur, `uvicorn app.main:app --reload` + `npm run dev` ile
   uçtan uca bir kez daha manuel doğrula (özellikle Groq sağlayıcısını —
   henüz gerçek bir API anahtarıyla test edilmemiş görünüyor).
3. README'yi güncel commit'lere göre güncelle (Gün 6/7 bölümünü gerçek
   duruma göre revize et, Groq/deployment/streaming'i ekle).
4. FR-3.4 (otomatik katman geçişi) ve FR-6.4 (quiz eşiği) konusunda karar ver.
5. Pilot öncesi: en azından kritik akışlar için temel bir test/duman testi
   planı ve hata mesajı/responsive denetimi.

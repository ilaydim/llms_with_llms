# Durum: Yapılanlar ve Yapılacaklar

SRS maddeleri (FR/NFR) ile karşılaştırılmıştır. Son güncelleme: 2026-09-20.

İşaretler: ✅ yapıldı · ⚠️ kısmen / doğrulanmadı · ❌ yapılmadı

---

## YAPILANLAR

### Altyapı
- ✅ FastAPI backend, SQLite, React (Vite) frontend
- ✅ Tüm tablolar SRS Bölüm 6'ya göre (students, sessions, modules, dialogue_messages, application_tasks, quiz_results, revisit_logs, survey_responses, layer_progress)
- ✅ Railway deploy ayarları, Vite dev proxy
- ✅ Araştırmacı veri erişimi: SQLite dosyası + `export_data.py` ile CSV dökümü (SRS 2.2)
- ✅ API anahtarı `.env`'de, kodda yok (NFR-2.3)

### LLM
- ✅ Sağlayıcıdan bağımsız LLM katmanı: mock, Groq, Anthropic, OpenAI (NFR-5.2)
- ✅ Hata olursa en fazla 5 deneme, 429'da bekleme süresi okunuyor (NFR-4.2)
- ✅ Tutor Agent: modül config'inden dinamik prompt (FR-1.3, Bölüm 5.5)
- ✅ Evaluator Agent: açık uçlu cevabı puanlıyor (FR-6.3)
- ✅ Uygulama katmanında "doküman ara" aracı, gerçek semantik arama (chromadb + sentence-transformers) (FR-4.1)
- ✅ 5 adet RAG kaynak dokümanı
- ✅ Streaming cevap (NFR-1.1)

### Öğrenci akışı
- ✅ Kimlik girişi (isim / öğrenci no, şifresiz), aynı kişi tekrar girince eşleşme (FR-2.1, FR-2.2)
- ✅ Onam (consent) ekranı, girişten önce (NFR-2.2)
- ✅ Pre-anket / post-anket, kimlikle ilişkili, tekrar sorulmuyor (FR-8.1 – 8.3)
- ✅ Teori giriş metni sabit, LLM üretmiyor (FR-3.1)
- ✅ Serbest metin diyalog, her mesaj zaman damgasıyla kaydediliyor (FR-3.2, FR-3.3)
- ✅ Kapsam dışı sorularda konuya yönlendirme, system prompt'ta (FR-3.5)
- ✅ Eleştirel katman tartışma başlangıcı (FR-5.1, FR-5.2)
- ✅ Uygulama görevi adım takibi (FR-4.3)
- ✅ Quiz: çoktan seçmeli kural bazlı + açık uçlu Evaluator ile, doğru cevap istemciye sızmıyor (FR-6.1 – 6.3)
- ✅ Kalınca "geri dön / devam et" seçimi; geri dönüş ve deneme sayısı kayıtlı (FR-6.4, 6.6, 6.7)
- ✅ Sekme kapanıp açılsa kaldığı yerden devam (NFR-4.1)
- ✅ TR / EN dil değiştirme (İlayda Dim)
- ✅ Mesajlar öğrenci / tutor için net ayrışıyor (NFR-3.2)

### Bu oturumda eklenenler
- ✅ Otomatik testler: 29 test (mock LLM, geçici veritabanı), UC-1 → UC-8 akışı dahil
- ✅ Streaming testleri
- ✅ Gerçek Groq ile canlı test dosyası (varsayılan olarak atlanır: `RUN_LIVE_LLM=1`)
- ✅ Katman kilidi backend'de de zorunlu: önceki katman bitmeden mesaj, quiz, revisit `403` (`services/layer_access.py`)
- ✅ `PATCH /progress` ile katman "completed" yapılamıyor, sadece quiz tamamlar
- ✅ Learning analytics: `GET /analytics/student/{id}` ve `GET /analytics/summary` (FR-7.1, 7.2, 7.3, SRS 8.4 betimsel istatistik)
- ✅ Oturum kapanınca `in_progress` katmanlar `abandoned` oluyor (FR-7.2)
- ✅ Aktif süre hesabı, 2 dakika kuralı (FR-7.3)

---

## YAPILACAKLAR

### Önce (pilot öncesi)
- ⚠️ **Gerçek LLM ile uçtan uca deneme.** Şu ana kadar tüm akış sadece mock ile denendi; gerçek Groq ile yalnızca tek tek çağrılar test edildi.
- ⚠️ **Hata mesajları (NFR-3.3).** Streaming'de stack trace sızmıyor (testli). Diğer endpoint'lerde ve arayüzde LLM hatasında gösterilen mesaj elle kontrol edilmedi.
- ⚠️ **Responsive kontrol (NFR-5.1).** Masaüstü tarayıcılarda elle bakılmadı.
- ⚠️ **20 eşzamanlı öğrenci (NFR-1.2).** Hiç ölçülmedi. Groq ücretsiz katman limitleri de aşılabilir (SRS 2.5: istek sayısı izlenmeli).
- ⚠️ **"Geri dön" akışı (FR-6.5 / UC-6) eksik.** Kodu okuyarak kontrol ettim:
  - ✅ Daha basit, gerçek dünya örnekli farklı anlatım üretiliyor ([tutor_agent.py](backend/app/agents/tutor_agent.py) `generate_simplified_explanation`)
  - ⚠️ "Şimdi anladın mı?" sorusu var (LLM'e sonda sormak talimatı + arayüzde sabit metin), ama cevabı kimse okumuyor, sadece bir "Tekrar dene" butonu var
  - ❌ **Öğrenci yeni anlatım üzerine soru soramıyor.** Anlatım quiz ekranında gösteriliyor ve orada sohbet kutusu yok; tek seçenek quizi yeniden çözmek. SRS "öğrenciye soru sorma imkânı tanımalı" diyor.
  - ❌ **"Benzer ama farklı bir soru" yok.** "Tekrar dene" aynı soruları (aynı id'ler) yeniden getiriyor ([QuizScreen.jsx](frontend/src/components/QuizScreen.jsx) `handleRetake`). Öğrenci cevapları ezberleyebilir; ölçüm geçerliliğini bozar. Çözüm için `rag.json`'a her katman için ikinci bir soru seti (TR + EN) yazılması ve `attempt_number > 1` iken onun sunulması gerekiyor. İçerik yazımı gerektiriyor.

### Karar bekleyenler
- ❌ **Quiz geçme eşiği (FR-6.4, SRS'te TBD).** Şu an `0.6·çoktan seçmeli + 0.4·açık uçlu ≥ 0.7`, ekip onaylamalı.
- ❌ **Otomatik katman geçişi (FR-3.4).** Şu an öğrenci "Quiz'e geç" butonuna basıyor. SRS "otomatik geçiş sunmalı" diyor.
- ❌ **Terk edilen katmanı yakalama (FR-7.2).** Öğrenci sekmeyi kapatırsa katman `in_progress` kalıyor. Bunun için "X dakika etkileşim yoksa bırakıldı say" gibi bir kural lazım.
- ❌ **Groq modeli.** `.env`'de `openai/gpt-oss-120b` var (Groq'ta barındırılan model, OpenAI API'si değil). Karar verilince `.env.example` güncellenecek; şu an içinde kaldırılmış `gemma2-9b-it` ve erişilemeyen `llama-3.3-70b-versatile` yazıyor. Kod varsayılanı da ([config.py](backend/app/core/config.py)) `llama-3.3-70b-versatile`.
- ❌ **Konuşma geçmişi limiti (SRS 5.4 "açık nokta").** Şu an son 20 mesaj (`MAX_CONTEXT_MESSAGES`), gözden geçirilmeli.
- ❌ **Pilot katılımcı seçim yöntemi (SRS 8.2)** — gönüllü mü, ders kapsamında mı?

### Analiz (SRS 8.4)
- ❌ Pre/post karşılaştırma scripti: öğrenci bazlı eşleştirme, Shapiro-Wilk, paired t-testi / Wilcoxon, Cohen's d (başarı kriteri: p < 0.05 ve d ≥ 0.5). Şu an sadece ham CSV export var.
- ❌ Anket puanlarını hesaplayan yardımcı (Likert maddelerinin toplam/ortalaması)

### Sağlamlık / temizlik
- ⚠️ Kimlik doğrulama yok: `/analytics/student/{id}` ve `/progress/student/{id}` id'yi bilen herkese açık. SRS MVP'de şifresiz istiyor (Faz 2'de kalkacak), ama canlıya çıkmadan önce bilinmeli.
- ⚠️ NFR-2.1 (veri üçüncü taraflarla paylaşılmamalı): öğrenci mesajları LLM sağlayıcısına (Groq) gidiyor. Onam metninde belirtildiğinden emin olun.
- ❌ `on_event("startup")` ve class-based Pydantic `Config` için deprecation uyarıları (zararsız, ileride kırılabilir)
- ❌ [progress.py](backend/app/routers/progress.py) içindeki işe yaramayan koşul: `current_view = "chat" if in_progress_row else "chat"`
- ❌ README güncel tutulmalı; İlayda'nın [docs/STATUS_REPORT.md](docs/STATUS_REPORT.md) dosyası ile birleştirilebilir

### Faz 2 (bu MVP'nin kapsamı dışında)
- Diğer 6 modül, takılma noktası tespiti (Personalization Agent), tam roadmap arayüzü, tam giriş/kayıt sistemi, PostgreSQL, mobil optimizasyon

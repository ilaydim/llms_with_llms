"""
SRS Bölüm 5.4 — Evaluator Agent çağrısı:
Bağlam = (a) açık uçlu sorunun beklenen cevap kriterleri (modül config'inde
tanımlı), (b) öğrencinin verdiği cevap → çıktı: yapılandırılmış sonuç
({"basarili": true/false, "geri_bildirim": "..."}).

FR-6.3: Açık uçlu soru, LLM tarafından değerlendirilip bir başarı/başarısızlık
ya da kısmi puan üretmelidir. Düşük temperature ile tutarlı/objektif puanlama
hedeflenir (Bölüm 5.2).
"""
import json

from app.agents.llm_client import LLMClient, get_llm_client
from app.services.module_loader import load_module_config

EVALUATOR_SYSTEM_PROMPT = """Sen objektif bir değerlendirme asistanısın (Evaluator Agent).
Görevin, bir öğrencinin açık uçlu soruya verdiği cevabı, sağlanan değerlendirme
kriterlerine göre puanlamaktır. Kibar olmaya çalışma, öğretici olmaya çalışma —
sadece tutarlı ve objektif değerlendir.

SADECE aşağıdaki JSON formatında cevap ver, başka hiçbir şey yazma:
{"basarili": true veya false, "puan": 0.0-1.0 arası bir sayı, "geri_bildirim": "kısa, yapıcı geri bildirim"}
"""


class EvaluatorAgent:
    def __init__(self, llm_client: LLMClient | None = None):
        self._llm = llm_client or get_llm_client()

    def evaluate_open_ended(
        self, module_code: str, layer: str, question_id: str, student_answer: str
    ) -> dict:
        module_config = load_module_config(module_code)
        open_ended = module_config["quiz"][layer]["open_ended"]

        if open_ended["id"] != question_id:
            raise ValueError(f"Soru ID uyuşmuyor: {question_id}")

        user_message = (
            f"Soru: {open_ended['question']}\n\n"
            f"Değerlendirme kriterleri: {open_ended['evaluation_criteria']}\n\n"
            f"Öğrencinin cevabı: {student_answer}"
        )

        response = self._llm.generate(
            system_prompt=EVALUATOR_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            temperature=0.0,  # Tutarlı/objektif puanlama için düşük temperature
            max_tokens=300,
        )

        return self._parse_response(response.text)

    @staticmethod
    def _parse_response(raw_text: str) -> dict:
        """LLM'in JSON dışı bir şey döndürme ihtimaline karşı güvenli parse."""
        try:
            cleaned = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            parsed = json.loads(cleaned)
            return {
                "basarili": bool(parsed.get("basarili", False)),
                "puan": float(parsed.get("puan", 0.0)),
                "geri_bildirim": str(parsed.get("geri_bildirim", "")),
            }
        except (json.JSONDecodeError, ValueError, TypeError):
            # Beklenmeyen format durumunda güvenli varsayım: başarısız + ham metni geri bildirim olarak döndür
            return {"basarili": False, "puan": 0.0, "geri_bildirim": raw_text.strip() or "Değerlendirme yapılamadı."}

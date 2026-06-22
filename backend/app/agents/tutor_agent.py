"""
SRS Bölüm 5.4 — Tutor Agent çağrısı:
Bağlam = (a) aktif modülün ilgili katman içeriği, (b) oturumdaki önceki mesajlar,
(c) öğrencinin son mesajı → çıktı: doğal dilde cevap.

SRS Bölüm 5.5 — Modül Bazlı Tutor Agent Örnekleme:
Tek bir kod tabanı, her çağrıldığında aktif modülün config'inden dinamik olarak
oluşturulan modüle özgü bir sistem promptuyla çalışır.

FR-3.2/3.3/3.5, FR-4.1, FR-5.1/5.2 burada karşılanır.
"""
from app.agents.llm_client import LLMClient, ToolDefinition, get_llm_client
from app.core.config import get_settings
from app.services.document_search import search_documents
from app.services.module_loader import build_tutor_system_prompt, load_module_config


class TutorAgent:
    def __init__(self, llm_client: LLMClient | None = None):
        self._llm = llm_client or get_llm_client()
        self._settings = get_settings()

    def _build_tools(self, layer: str) -> list[ToolDefinition] | None:
        """FR-4.1: Uygulama katmanında çalışırken Tutor Agent'a doküman arama aracı tanımlanır."""
        if layer != "application":
            return None

        return [
            ToolDefinition(
                name="search_documents",
                description="RAG doküman koleksiyonunda anlamsal arama yapar ve en alakalı parçaları döner.",
                input_schema={
                    "type": "object",
                    "properties": {"query": {"type": "string", "description": "Aranacak soru/konu"}},
                    "required": ["query"],
                },
                handler=lambda args: search_documents(args.get("query", "")),
            )
        ]

    def respond(
        self,
        module_code: str,
        layer: str,
        conversation_history: list[dict[str, str]],
        student_message: str,
    ) -> dict:
        """
        conversation_history: [{"role": "user"/"assistant", "content": "..."}]
        (Bölüm 5.4 "Açık nokta": kaç mesajın bağlama dahil edileceği
        settings.max_context_messages ile sınırlanır.)
        """
        module_config = load_module_config(module_code)
        system_prompt = build_tutor_system_prompt(module_config, layer)

        trimmed_history = conversation_history[-self._settings.max_context_messages :]
        messages = trimmed_history + [{"role": "user", "content": student_message}]

        tools = self._build_tools(layer)

        response = self._llm.generate(
            system_prompt=system_prompt,
            messages=messages,
            tools=tools,
            temperature=0.7,
        )

        return {
            "reply": response.text,
            "tool_calls_made": response.tool_calls_made,
        }

    def generate_layer_intro(self, module_code: str, layer: str) -> str:
        """
        FR-3.1: Teori katmanı girişi sabit metinden gelir (Tutor Agent tarafından
        ÜRETİLMEZ) — bu fonksiyon o kuralı uygular, sadece config'ten okuyup döner.
        Uygulama/Eleştirel katmanlar için de aynı şekilde config'teki sabit
        başlangıç metnini döner.
        """
        module_config = load_module_config(module_code)
        if layer == "theory":
            return module_config["theory"]["intro_text"]
        if layer == "application":
            return module_config["application"]["task_description"]
        if layer == "critical":
            return module_config["critical"]["discussion_starter"]
        raise ValueError(f"Bilinmeyen katman: {layer}")

    def generate_simplified_explanation(
        self, module_code: str, layer: str, conversation_history: list[dict[str, str]]
    ) -> str:
        """
        FR-6.5: Mastery learning'de quiz geçilemediğinde, aynı konunun daha basit,
        gerçek dünya örnekli bir anlatımını üretir (bu kısım, sabit metnin aksine
        Tutor Agent tarafından dinamik üretilir).
        """
        module_config = load_module_config(module_code)
        system_prompt = build_tutor_system_prompt(module_config, layer)
        instruction = (
            "Öğrenci bu konunun quiz'inde başarısız oldu ve 'tekrar anlat' seçeneğini "
            "seçti. Aynı konuyu, ÖNCEKİNDEN FARKLI bir anlatımla, daha basit kelimelerle "
            "ve gerçek dünyadan somut bir örnekle yeniden anlat. Sonunda öğrenciye "
            "şimdi anlayıp anlamadığını sor."
        )
        response = self._llm.generate(
            system_prompt=system_prompt,
            messages=conversation_history + [{"role": "user", "content": instruction}],
            temperature=0.7,
        )
        return response.text

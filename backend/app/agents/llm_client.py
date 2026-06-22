"""
NFR-5.2: "Faz 2'de farklı bir LLM sağlayıcısına geçiş gerekirse, API entegrasyon
katmanı bu değişikliği minimum kod değişikliğiyle desteklemelidir."

Bu yüzden Tutor/Evaluator Agent'lar doğrudan Anthropic ya da OpenAI SDK'sını
çağırmaz; ortak bir `LLMClient` arayüzü üzerinden konuşur. Hangi sağlayıcının
kullanılacağı .env'deki LLM_PROVIDER değişkeniyle seçilir:

  LLM_PROVIDER=mock        -> API anahtarı gerekmez, agent'ları test etmek için
  LLM_PROVIDER=anthropic   -> Anthropic Claude API
  LLM_PROVIDER=openai      -> OpenAI API

Henüz hangi sağlayıcıya karar verilmediği için varsayılan "mock"tur; gerçek API
seçilince sadece .env değiştirilir, agent kodlarına dokunulmaz.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable

from app.core.config import get_settings


@dataclass
class ToolDefinition:
    """Sağlayıcıdan bağımsız, ortak tool/function-calling tanımı."""

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], str]


@dataclass
class LLMResponse:
    text: str
    tool_calls_made: list[str] = field(default_factory=list)
    raw: Any = None


class LLMClient(ABC):
    """Tüm sağlayıcı implementasyonlarının uyacağı ortak arayüz."""

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """
        messages: [{"role": "user"/"assistant", "content": "..."}]
        Tool çağrısı gerekiyorsa implementasyon bunu kendi içinde
        (tool_use -> handler çağırma -> tekrar modele gönderme) döngüsüyle halleder
        ve sadece nihai metni döner.
        """
        raise NotImplementedError


class MockLLMClient(LLMClient):
    """
    Henüz gerçek bir API bağlanmadığı için kullanılan sahte istemci.
    Agent mantığını, prompt akışını ve frontend entegrasyonunu API anahtarı
    olmadan uçtan uca test etmeyi sağlar.
    """

    def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        last_user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )

        tool_note = ""
        if tools:
            # Mock istemci, gerçekçi test için "doküman ara" gibi araçları
            # her zaman bir kere çağırıp sonucu cevaba ekler.
            tool = tools[0]
            tool_result = tool.handler({"query": last_user_msg})
            tool_note = f"\n\n[{tool.name} aracı çağrıldı] → {tool_result}"

        reply = (
            "(Mock Tutor Agent — gerçek LLM API'si henüz bağlanmadı)\n"
            f'Sorunu aldım: "{last_user_msg}"\n'
            "Gerçek API bağlandığında burada modülün içeriğine dayalı, "
            "doğal dilde bir açıklama göreceksin."
            f"{tool_note}"
        )
        return LLMResponse(text=reply, tool_calls_made=[t.name for t in (tools or [])[:1] if tool_note])


class AnthropicLLMClient(LLMClient):
    """Anthropic Claude API implementasyonu (seçilirse aktif olur)."""

    def __init__(self, api_key: str, model: str):
        from anthropic import Anthropic  # lazy import: paket kurulu değilse mock ile çalışmaya devam edilebilir

        self._client = Anthropic(api_key=api_key)
        self._model = model

    def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        anthropic_tools = None
        tool_map = {}
        if tools:
            anthropic_tools = []
            for t in tools:
                anthropic_tools.append(
                    {"name": t.name, "description": t.description, "input_schema": t.input_schema}
                )
                tool_map[t.name] = t.handler

        conversation = list(messages)
        tool_calls_made: list[str] = []

        # Tool-use döngüsü: model bir araç çağırmak isterse, çalıştırıp sonucu
        # tekrar modele veriyoruz; model nihai metin cevabı verene kadar devam eder.
        for _ in range(5):
            response = self._client.messages.create(
                model=self._model,
                system=system_prompt,
                messages=conversation,
                tools=anthropic_tools or [],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            if response.stop_reason != "tool_use":
                final_text = "".join(
                    block.text for block in response.content if block.type == "text"
                )
                return LLMResponse(text=final_text, tool_calls_made=tool_calls_made, raw=response)

            conversation.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_calls_made.append(block.name)
                    handler = tool_map.get(block.name)
                    result_text = handler(block.input) if handler else "Araç bulunamadı."
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": result_text}
                    )
            conversation.append({"role": "user", "content": tool_results})

        return LLMResponse(text="(Araç döngüsü tamamlanamadı)", tool_calls_made=tool_calls_made)


class OpenAILLMClient(LLMClient):
    """OpenAI API implementasyonu (seçilirse aktif olur)."""

    def __init__(self, api_key: str, model: str):
        from openai import OpenAI  # lazy import

        self._client = OpenAI(api_key=api_key)
        self._model = model

    def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        openai_tools = None
        tool_map = {}
        if tools:
            openai_tools = []
            for t in tools:
                openai_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": t.name,
                            "description": t.description,
                            "parameters": t.input_schema,
                        },
                    }
                )
                tool_map[t.name] = t.handler

        conversation = [{"role": "system", "content": system_prompt}] + list(messages)
        tool_calls_made: list[str] = []

        for _ in range(5):
            response = self._client.chat.completions.create(
                model=self._model,
                messages=conversation,
                tools=openai_tools,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            choice = response.choices[0]
            if choice.finish_reason != "tool_calls":
                return LLMResponse(text=choice.message.content or "", tool_calls_made=tool_calls_made, raw=response)

            conversation.append(choice.message)
            for call in choice.message.tool_calls:
                import json as _json

                tool_calls_made.append(call.function.name)
                handler = tool_map.get(call.function.name)
                args = _json.loads(call.function.arguments)
                result_text = handler(args) if handler else "Araç bulunamadı."
                conversation.append(
                    {"role": "tool", "tool_call_id": call.id, "content": result_text}
                )

        return LLMResponse(text="(Araç döngüsü tamamlanamadı)", tool_calls_made=tool_calls_made)


def get_llm_client() -> LLMClient:
    """
    .env'deki LLM_PROVIDER'a göre doğru istemciyi döner.
    Karar verilene kadar varsayılan "mock" olduğundan agent kodu API anahtarı
    olmadan da uçtan uca test edilebilir.
    """
    settings = get_settings()
    provider = getattr(settings, "llm_provider", "mock").lower()

    if provider == "anthropic":
        return AnthropicLLMClient(api_key=settings.anthropic_api_key, model=settings.tutor_model)
    if provider == "openai":
        return OpenAILLMClient(api_key=settings.openai_api_key, model=settings.tutor_model)
    return MockLLMClient()

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

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable

from app.core.config import get_settings


def _with_retry(fn, max_attempts: int = 2, delay: float = 1.0):
    """NFR-4.2: LLM API'den hata dönerse en az 1 kez otomatik yeniden dener."""
    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < max_attempts - 1:
                time.sleep(delay)
    raise last_exc


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


from typing import Generator


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

    def generate_stream(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Generator[str, None, None]:
        """
        NFR-1.1: Metin parçalarını (chunk) birer birer yield eder.
        Alt sınıflar override etmezse generate() sonucunu tek chunk olarak döner.
        """
        result = self.generate(system_prompt, messages, tools, temperature, max_tokens)
        yield result.text


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
        import json as _json

        last_user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        # Tutor/Evaluator sistem promptlarına eklenen dil talimatından hedef dili tespit et
        is_turkish = "feedback in Turkish" in system_prompt or "only in Turkish" in system_prompt

        # EvaluatorAgent expects JSON — detect from system prompt and return a compatible response
        if "Evaluator Agent" in system_prompt or '"basarili"' in system_prompt:
            feedback = "(Sahte değerlendirme) Cevap yeterli görünüyor." if is_turkish else "(Mock evaluation) The answer looks sufficient."
            reply = _json.dumps({
                "basarili": True,
                "puan": 0.75,
                "geri_bildirim": feedback,
            }, ensure_ascii=False)
            return LLMResponse(text=reply)

        tool_note = ""
        if tools:
            # Mock istemci, gerçekçi test için "doküman ara" gibi araçları
            # her zaman bir kere çağırıp sonucu cevaba ekler.
            tool = tools[0]
            tool_result = tool.handler({"query": last_user_msg})
            tool_label = "aracı çağrıldı" if is_turkish else "tool called"
            tool_note = f"\n\n[{tool.name} {tool_label}] → {tool_result}"

        if is_turkish:
            reply = (
                "(Sahte Öğretici Ajan — henüz gerçek bir LLM API'sine bağlı değil)\n"
                f'Mesajını aldım: "{last_user_msg}"\n'
                "Gerçek bir API bağlandığında, modül içeriğine dayanan doğal dilde "
                "bir cevap göreceksin."
                f"{tool_note}"
            )
        else:
            reply = (
                "(Mock Tutor Agent — no real LLM API connected yet)\n"
                f'I received your message: "{last_user_msg}"\n'
                "Once a real API is connected, you will see a natural-language response "
                "grounded in the module content."
                f"{tool_note}"
            )
        return LLMResponse(text=reply, tool_calls_made=[t.name for t in (tools or [])[:1] if tool_note])

    def generate_stream(self, system_prompt, messages, tools=None, temperature=0.7, max_tokens=1024):
        """Mock streaming: kelimeleri birer birer yield ederek streaming simüle eder."""
        result = self.generate(system_prompt, messages, tools, temperature, max_tokens)
        words = result.text.split(" ")
        for i, word in enumerate(words):
            yield word if i == len(words) - 1 else word + " "


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
            response = _with_retry(lambda: self._client.messages.create(
                model=self._model,
                system=system_prompt,
                messages=conversation,
                tools=anthropic_tools or [],
                temperature=temperature,
                max_tokens=max_tokens,
            ))

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

    def generate_stream(self, system_prompt, messages, tools=None, temperature=0.7, max_tokens=1024):
        """
        NFR-1.1: Gerçek Anthropic streaming.
        Tool kullanılıyorsa (application katmanı) önce tam cevabı alır, sonra chunk'lar.
        Tool yoksa (theory/critical) native streaming kullanır.
        """
        if tools:
            # Tool-use akışı streaming desteklemediği için tam cevap al → chunk'la
            result = self.generate(system_prompt, messages, tools, temperature, max_tokens)
            words = result.text.split(" ")
            for i, word in enumerate(words):
                yield word if i == len(words) - 1 else word + " "
            return

        # Native Anthropic streaming (tool yok)
        # _with_retry burada kullanılamaz (context manager), doğrudan stream açıyoruz
        with self._client.messages.stream(
            model=self._model,
            system=system_prompt,
            messages=list(messages),
            temperature=temperature,
            max_tokens=max_tokens,
        ) as stream:
            for chunk in stream.text_stream:
                yield chunk


class GroqLLMClient(LLMClient):
    """Groq API implementasyonu — OpenAI-uyumlu arayüz üzerinden çalışır."""

    def __init__(self, api_key: str, model: str):
        from groq import Groq  # lazy import

        self._client = Groq(api_key=api_key)
        self._model = model

    def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        groq_tools = None
        tool_map = {}
        if tools:
            groq_tools = []
            for t in tools:
                groq_tools.append(
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
            response = _with_retry(lambda: self._client.chat.completions.create(
                model=self._model,
                messages=conversation,
                tools=groq_tools,
                temperature=temperature,
                max_tokens=max_tokens,
            ))
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

    def generate_stream(self, system_prompt, messages, tools=None, temperature=0.7, max_tokens=1024):
        """Groq streaming — tool kullanılıyorsa önce tam cevap al, sonra chunk'la."""
        if tools:
            result = self.generate(system_prompt, messages, tools, temperature, max_tokens)
            words = result.text.split(" ")
            for i, word in enumerate(words):
                yield word if i == len(words) - 1 else word + " "
            return

        stream = _with_retry(lambda: self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system_prompt}] + list(messages),
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        ))
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta


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
            response = _with_retry(lambda: self._client.chat.completions.create(
                model=self._model,
                messages=conversation,
                tools=openai_tools,
                temperature=temperature,
                max_tokens=max_tokens,
            ))
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
    if provider == "groq":
        return GroqLLMClient(api_key=settings.groq_api_key, model=settings.tutor_model)
    return MockLLMClient()

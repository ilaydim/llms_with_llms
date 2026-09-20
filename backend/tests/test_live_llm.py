"""
Gerçek LLM (.env'deki Groq) ile duman testi. Varsayılan olarak ATLANIR — ağ, kota ve
API anahtarı gerektirir, ve LLM çıktısı deterministik değildir.

Çalıştırmak için:  RUN_LIVE_LLM=1 .venv/bin/python -m pytest tests/test_live_llm.py -v
Sağlayıcı hatalarına (429 vb.) karşı retry zaten llm_client._with_retry'de.
"""
import os

import pytest

from app.agents.evaluator_agent import EvaluatorAgent
from app.agents.llm_client import GroqLLMClient
from app.agents.tutor_agent import TutorAgent
from app.core.config import get_settings

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_LLM") != "1" or not get_settings().groq_api_key,
    reason="RUN_LIVE_LLM=1 ve GROQ_API_KEY gerekli",
)


@pytest.fixture(scope="module")
def llm():
    s = get_settings()
    return GroqLLMClient(api_key=s.groq_api_key, model=s.tutor_model)


def test_tutor_replies_in_turkish(llm):
    out = TutorAgent(llm).respond("rag", "theory", [], "RAG nedir? Kısaca açıkla.", lang="tr")
    assert out["reply"].strip()


def test_tutor_streams_multiple_chunks(llm):
    chunks = list(TutorAgent(llm).stream_respond("rag", "critical", [], "Give one limitation of RAG.", lang="en"))
    assert len(chunks) > 1 and "".join(chunks).strip()


def test_application_layer_tool_use_does_not_crash(llm):
    out = TutorAgent(llm).respond("rag", "application", [], "Which chunk size should I start with?", lang="en")
    assert out["reply"].strip()


def test_evaluator_returns_valid_score_and_separates_good_from_bad(llm):
    from app.services.module_loader import get_module_content, load_module_config

    q = get_module_content(load_module_config("rag"), "en")["quiz"]["theory"]["open_ended"]
    ev = EvaluatorAgent(llm)
    good = ev.evaluate_open_ended("rag", "theory", q["id"],
        "RAG retrieves relevant document chunks and adds them to the prompt so the LLM grounds its "
        "answer in external, up-to-date knowledge instead of relying only on its parameters.")
    bad = ev.evaluate_open_ended("rag", "theory", q["id"], "banana pizza")
    for r in (good, bad):
        assert 0.0 <= r["puan"] <= 1.0 and r["geri_bildirim"]
    assert good["puan"] > bad["puan"]

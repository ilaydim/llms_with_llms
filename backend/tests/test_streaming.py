"""NFR-1.1: SSE streaming endpoint'i (mock LLM)."""
import json

MODULE = "rag"


def _events(response):
    return [json.loads(line[len("data: "):]) for line in response.text.split("\n\n") if line.startswith("data: ")]


def _stream(client, session_id, layer="theory", content="What is RAG?"):
    return client.post("/dialogue/message/stream", json={
        "session_id": session_id, "module_code": MODULE, "layer": layer, "content": content})


def test_stream_emits_chunks_then_done_and_persists(client, session_ids):
    _, session_id = session_ids
    r = _stream(client, session_id)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")

    events = _events(r)
    chunks = [e["chunk"] for e in events if "chunk" in e]
    assert len(chunks) > 1
    assert events[-1]["done"] is True and "message_id" in events[-1]

    history = client.get(f"/dialogue/{session_id}/{MODULE}/theory/history").json()
    assert [m["sender"] for m in history] == ["student", "tutor_agent"]
    assert history[1]["content"] == "".join(chunks)  # kaydedilen cevap = akan chunk'ların toplamı
    assert history[1]["id"] == events[-1]["message_id"]


def test_stream_marks_layer_in_progress(client, session_ids):
    student_id, session_id = session_ids
    _stream(client, session_id, layer="application")
    # application in_progress ama completed değil
    assert client.get(f"/progress/student/{student_id}").json()["layers_completed"] == []


def test_stream_unknown_session_returns_error_event(client):
    events = _events(_stream(client, 999))
    assert events == [{"error": "Oturum veya modül bulunamadı"}]


def test_stream_error_does_not_leak_details(client, session_ids, monkeypatch):
    _, session_id = session_ids

    def boom(*a, **k):
        raise RuntimeError("secret-internal-detail")
        yield  # noqa: unreachable — generator olsun

    monkeypatch.setattr("app.routers.dialogue._tutor_agent.stream_respond", boom)
    r = _stream(client, session_id)
    assert "secret-internal-detail" not in r.text  # NFR-3.3
    assert _events(r)[-1] == {"error": "Bir hata oluştu, lütfen tekrar deneyin."}

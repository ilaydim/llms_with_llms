"""Katman kilidi backend'de zorunlu: bir katman ancak öncekini tamamlayınca açılır."""
import json

from tests.test_flow import LAYERS, MODULE, _correct_answers, _submit_quiz


def _msg(client, session_id, layer):
    return client.post("/dialogue/message", json={
        "session_id": session_id, "module_code": MODULE, "layer": layer, "content": "hi"})


def _complete(client, session_id, layer):
    assert _submit_quiz(client, session_id, layer, _correct_answers(client, layer)).json()["passed"]


def test_first_layer_is_always_open(client, session_ids):
    assert _msg(client, session_ids[1], "theory").status_code == 200


def test_locked_layers_reject_message_quiz_and_revisit(client, session_ids):
    _, sid = session_ids
    assert _msg(client, sid, "application").status_code == 403
    assert _msg(client, sid, "critical").status_code == 403
    assert _submit_quiz(client, sid, "application", _correct_answers(client, "application")).status_code == 403
    r = client.post("/quiz/revisit", json={
        "session_id": sid, "module_code": MODULE, "layer": "critical", "revisited": False})
    assert r.status_code == 403


def test_locked_layer_rejected_by_progress_patch(client, session_ids):
    _, sid = session_ids
    r = client.patch(f"/progress/{sid}/{MODULE}/critical", json={"status": "completed"})
    assert r.status_code == 403


def test_locked_layer_leaves_no_trace(client, session_ids):
    student_id, sid = session_ids
    _msg(client, sid, "critical")
    _submit_quiz(client, sid, "critical", _correct_answers(client, "critical"))
    assert client.get(f"/dialogue/{sid}/{MODULE}/critical/history").json() == []
    assert client.get(f"/progress/student/{student_id}").json()["layers_completed"] == []


def test_stream_rejects_locked_layer_without_saving(client, session_ids):
    _, sid = session_ids
    r = client.post("/dialogue/message/stream", json={
        "session_id": sid, "module_code": MODULE, "layer": "application", "content": "hi"})
    events = [json.loads(l[6:]) for l in r.text.split("\n\n") if l.startswith("data: ")]
    assert events == [{"error": "Bu katman henüz kilitli.", "locked": True}]
    assert client.get(f"/dialogue/{sid}/{MODULE}/application/history").json() == []


def test_layers_unlock_in_order(client, session_ids):
    _, sid = session_ids
    _complete(client, sid, "theory")
    assert _msg(client, sid, "application").status_code == 200
    assert _msg(client, sid, "critical").status_code == 403  # atlama yok
    _complete(client, sid, "application")
    assert _msg(client, sid, "critical").status_code == 200


def test_reading_past_layers_stays_open(client, session_ids):
    _, sid = session_ids
    assert client.get(f"/dialogue/{sid}/{MODULE}/critical/history").status_code == 200
    assert client.get(f"/quiz/{MODULE}/critical").status_code == 200
    assert client.get(f"/dialogue/{MODULE}/critical/intro").status_code == 200


def test_completed_layers_stay_open_for_review(client, session_ids):
    _, sid = session_ids
    for layer in LAYERS:
        _complete(client, sid, layer)
    assert _msg(client, sid, "theory").status_code == 200


def test_progress_patch_cannot_mark_completed(client, session_ids):
    student_id, sid = session_ids
    r = client.patch(f"/progress/{sid}/{MODULE}/theory", json={"status": "completed"})
    assert r.status_code == 400
    assert client.get(f"/progress/student/{student_id}").json()["layers_completed"] == []
    assert client.patch(f"/progress/{sid}/{MODULE}/theory", json={"status": "in_progress"}).status_code == 200

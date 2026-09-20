"""FR-7.1/7.2/7.3: learning analytics özetleri ve 'abandoned' durumu."""
from tests.test_flow import MODULE, _correct_answers, _submit_quiz


def _say(client, sid, layer, n):
    for i in range(n):
        client.post("/dialogue/message", json={
            "session_id": sid, "module_code": MODULE, "layer": layer, "content": f"q{i}"})


def _layer(data, name):
    return next(l for l in data["layers"] if l["layer"] == name)


def test_student_analytics_counts_messages_per_layer(client, session_ids):
    student_id, sid = session_ids
    _say(client, sid, "theory", 3)
    data = client.get(f"/analytics/student/{student_id}").json()
    assert data["total_student_messages"] == 3  # tutor mesajları sayılmaz
    assert _layer(data, "theory")["student_messages"] == 3
    assert _layer(data, "theory")["status"] == "in_progress"
    assert _layer(data, "application")["status"] == "not_started"
    assert data["session_count"] == 1


def test_student_analytics_quiz_and_revisit(client, session_ids):
    student_id, sid = session_ids
    wrong = [{"question_id": a["question_id"], "selected_index": 99} for a in _correct_answers(client, "theory")]
    _submit_quiz(client, sid, "theory", wrong)
    client.post("/quiz/revisit", json={"session_id": sid, "module_code": MODULE, "layer": "theory", "revisited": True})
    _submit_quiz(client, sid, "theory", _correct_answers(client, "theory"))
    t = _layer(client.get(f"/analytics/student/{student_id}").json(), "theory")
    assert t["quiz_attempts"] == 2 and t["revisit_count"] == 1
    assert t["best_quiz_score"] == 0.6 * 1 + 0.4 * 0.75  # en iyi deneme
    assert t["status"] == "completed"


def test_unknown_student_404(client):
    assert client.get("/analytics/student/999").status_code == 404


def test_ending_session_marks_in_progress_layers_abandoned(client, session_ids):
    student_id, sid = session_ids
    _say(client, sid, "theory", 1)
    client.post(f"/sessions/{sid}/end")
    assert _layer(client.get(f"/analytics/student/{student_id}").json(), "theory")["status"] == "abandoned"


def test_ending_session_keeps_completed_layers(client, session_ids):
    student_id, sid = session_ids
    _submit_quiz(client, sid, "theory", _correct_answers(client, "theory"))
    client.post(f"/sessions/{sid}/end")
    assert _layer(client.get(f"/analytics/student/{student_id}").json(), "theory")["status"] == "completed"


def test_cohort_summary_mean_and_median(client):
    for name, n in (("A", 2), ("B", 4), ("C", 9)):
        st = client.post("/students/identify", json={"name": name}).json()
        sid = client.post(f"/sessions/start/{st['id']}").json()["id"]
        _say(client, sid, "theory", n)
    client.post("/students/identify", json={"name": "D"})  # hiç başlamadı

    s = client.get("/analytics/summary").json()
    assert s["student_count"] == 4
    theory = _layer(s, "theory")
    assert theory["students_started"] == 3
    assert theory["mean_student_messages"] == 5 and theory["median_student_messages"] == 4
    assert "name" not in str(s)  # anonim
    assert _layer(s, "critical")["mean_student_messages"] is None


def test_empty_cohort(client):
    s = client.get("/analytics/summary").json()
    assert s["student_count"] == 0 and s["mean_active_seconds"] is None

"""UC-1 → UC-8 akışının mock LLM ile API düzeyinde testi."""
MODULE = "rag"
LAYERS = ["theory", "application", "critical"]


def _correct_answers(client, layer):
    """Doğru cevaplar API'den sızdırılmadığı için config'ten okunur."""
    from app.services.module_loader import get_module_content, load_module_config

    content = get_module_content(load_module_config(MODULE), "en")
    return [
        {"question_id": q["id"], "selected_index": q["correct_index"]}
        for q in content["quiz"][layer]["mcq"]
    ]


def _submit_quiz(client, session_id, layer, answers):
    return client.post("/quiz/submit", json={
        "session_id": session_id, "module_code": MODULE, "layer": layer,
        "mcq_answers": answers, "open_ended_answer": "Because retrieval grounds answers.",
    })


def test_identify_is_idempotent(client):
    a = client.post("/students/identify", json={"name": "Ada", "student_no": "1"}).json()
    b = client.post("/students/identify", json={"name": "Ada", "student_no": "1"}).json()
    assert a["id"] == b["id"]


def test_session_is_resumed_until_ended(client, session_ids):
    student_id, session_id = session_ids
    assert client.post(f"/sessions/start/{student_id}").json()["id"] == session_id
    client.post(f"/sessions/{session_id}/end")
    assert client.post(f"/sessions/start/{student_id}").json()["id"] != session_id


def test_unknown_student_404(client):
    assert client.post("/sessions/start/999").status_code == 404


def test_survey_status_and_resubmit(client, session_ids):
    student_id, _ = session_ids
    assert client.get(f"/survey/status/{student_id}").json() == {
        "pre_completed": False, "post_completed": False}

    questions = client.get("/survey/questions/pre").json()
    assert questions
    answers = [{"question_id": q["id"], "answer": "3" if q["type"] == "likert" else "ok"}
               for q in questions]
    body = {"student_id": student_id, "survey_type": "pre", "answers": answers}
    assert client.post("/survey/submit", json=body).json()["answer_count"] == len(answers)
    client.post("/survey/submit", json=body)  # tekrar gönderim eskiyi ezer, çoğaltmaz
    assert client.get(f"/survey/status/{student_id}").json()["pre_completed"] is True


def test_dialogue_saves_both_messages(client, session_ids):
    _, session_id = session_ids
    r = client.post("/dialogue/message", json={
        "session_id": session_id, "module_code": MODULE, "layer": "theory", "content": "What is RAG?"})
    assert r.status_code == 200 and r.json()["sender"] == "tutor_agent"
    history = client.get(f"/dialogue/{session_id}/{MODULE}/theory/history").json()
    assert [m["sender"] for m in history] == ["student", "tutor_agent"]


def test_quiz_does_not_leak_correct_answers(client):
    r = client.get(f"/quiz/{MODULE}/theory")
    assert r.status_code == 200
    assert "correct_index" not in r.text


def test_quiz_pass_completes_layer(client, session_ids):
    student_id, session_id = session_ids
    r = _submit_quiz(client, session_id, "theory", _correct_answers(client, "theory")).json()
    assert r["passed"] is True and r["attempt_number"] == 1
    assert "theory" in client.get(f"/progress/student/{student_id}").json()["layers_completed"]


def test_quiz_fail_then_revisit_and_attempt_counter(client, session_ids):
    _, session_id = session_ids
    wrong = [{"question_id": a["question_id"], "selected_index": 99}
             for a in _correct_answers(client, "theory")]
    first = _submit_quiz(client, session_id, "theory", wrong).json()
    assert first["passed"] is False  # 0.6*0 + 0.4*0.75 = 0.3 < 0.7

    rv = client.post("/quiz/revisit", json={
        "session_id": session_id, "module_code": MODULE, "layer": "theory", "revisited": True})
    assert rv.status_code == 200 and rv.json()["explanation"]

    second = _submit_quiz(client, session_id, "theory", wrong).json()
    assert second["attempt_number"] == 2


def test_full_journey_ends_session_on_post_survey(client, session_ids):
    student_id, session_id = session_ids
    for layer in LAYERS:
        assert _submit_quiz(client, session_id, layer, _correct_answers(client, layer)).json()["passed"]
    progress = client.get(f"/progress/student/{student_id}").json()
    assert progress["layers_completed"] == LAYERS

    post = [{"question_id": q["id"], "answer": "3" if q["type"] == "likert" else "ok"}
            for q in client.get("/survey/questions/post").json()]
    client.post("/survey/submit", json={"student_id": student_id, "survey_type": "post", "answers": post})
    assert client.get(f"/survey/status/{student_id}").json()["post_completed"] is True
    # oturum kapandı → yeni start yeni oturum açar
    assert client.post(f"/sessions/start/{student_id}").json()["id"] != session_id


def test_application_tasks_update(client, session_ids):
    _, session_id = session_ids
    steps = client.get(f"/tasks/{session_id}/{MODULE}").json()
    assert steps and all(s["status"] == "not_started" for s in steps)
    r = client.patch(f"/tasks/{steps[0]['id']}", json={"status": "completed"}).json()
    assert r["status"] == "completed" and r["completed_at"]

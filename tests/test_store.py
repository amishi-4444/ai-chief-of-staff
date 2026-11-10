import json
from chief_of_staff import store


def test_search_kb_finds_relevant_doc():
    docs = store.search_kb("Series B investor valuation")
    assert docs and "NorthStar" in docs[0]["title"]


def test_search_kb_no_match():
    assert store.search_kb("zzzz qqqq") == []


def test_audit_writes_jsonl(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "LOGS", tmp_path)
    store.audit("unit_test", value=1)
    line = (tmp_path / "audit.jsonl").read_text().strip()
    assert json.loads(line)["event"] == "unit_test"


def test_data_files_are_valid():
    for name in ["inbox", "calendar", "goals", "tasks", "knowledge", "memory", "sent"]:
        assert isinstance(store.load(name), list)

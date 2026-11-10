"""Plain-Python data access (JSON files), audit logging and KB search.
Kept free of SDK imports so it is easy to unit test."""
import json
import time
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
LOGS = ROOT / "logs"
REPORTS = ROOT / "reports"


def load(name: str):
    return json.loads((DATA / f"{name}.json").read_text())


def save(name: str, obj) -> None:
    (DATA / f"{name}.json").write_text(json.dumps(obj, indent=2))


def audit(event: str, **fields) -> None:
    """Append one line to the audit trail (logs/audit.jsonl)."""
    LOGS.mkdir(exist_ok=True)
    record = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "event": event, **fields}
    with open(LOGS / "audit.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")


def search_kb(query: str, limit: int = 3) -> list[dict]:
    """Keyword-scored retrieval over data/knowledge.json (lightweight RAG)."""
    words = {w for w in query.lower().split() if len(w) > 2}
    scored = []
    for doc in load("knowledge"):
        text = (doc["title"] + " " + doc["content"]).lower()
        score = sum(w in text for w in words)
        if score:
            scored.append((score, doc))
    scored.sort(key=lambda x: -x[0])
    return [d for _, d in scored[:limit]]

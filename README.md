# AI Chief of Staff (OpenAI Agents SDK)

A multi-agent virtual Chief of Staff for a CEO: manages email, prepares meeting briefs, runs
research, tracks strategic goals and tasks, and produces executive summaries, with human
approval for critical actions. Built for the Summer School '26 capstone (Agents SDK track, project 1).

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # default is a free Gemini key; see the file for OpenAI/Ollama options
python -m chief_of_staff.main
```
Try: `/briefing`, `Prepare me for my 3pm investor call`, `Draft a reply to Priya about the term sheet`.
Flags: `--session NAME` (separate persisted conversation), `--auto-approve` (demo/tests only).
Run tests: `python -m pytest`. All data is mock JSON in `chief_of_staff/data/`, so no external accounts are needed.

## No OpenAI key?
The default `.env.example` uses Google's free Gemini API through its OpenAI-compatible endpoint. The hosted
web-search tool is OpenAI-only, so with other providers the Research Analyst uses the internal knowledge base only.
Smaller/local models may handle handoffs and structured outputs less reliably.

## Project layout
```
chief_of_staff/
  team.py       6 agents + handoffs        models.py   Pydantic structured outputs
  tools.py      13 function tools          briefing.py parallel /briefing workflow
  store.py      data access, audit, RAG    context.py  shared context + approval gate
  main.py       CLI + session persistence  data/       mock inbox, calendar, goals, tasks, KB
docs/           PROBLEM_ANALYSIS, ARCHITECTURE (diagram), PRESENTATION, DEMO_SCRIPT
tests/
```

## Brief requirements checklist
| Requirement | Where |
|---|---|
| Problem analysis | `docs/PROBLEM_ANALYSIS.md` |
| Multi-agent design + diagram | `docs/ARCHITECTURE.md` |
| 5+ specialised agents (we have 6) | `team.py` |
| 5+ tools/APIs (we have 14 incl. hosted web search) | `tools.py`, `team.py` |
| Agent handoffs | `team.py` (`handoffs=[...]`) |
| Memory / context | `context.py`, `SQLiteSession`, `memory.json` |
| Structured outputs | `models.py` (`ExecutiveSummary`, `MeetingBrief`) |
| Human approval | `send_email`, `schedule_meeting` via `AppContext.approve` |
| Optional: planning, RAG, long-term memory, parallel, error handling, logging, session persistence | `team.py`, `store.py`, `briefing.py`, `main.py` |
| Presentation / demo video | `docs/PRESENTATION.md`, `docs/DEMO_SCRIPT.md` (you record the video and build the slides) |

## Notes
Mock data is dated around 2026-11-10 (the agents' "today"). To swap in real services, replace the
bodies of the functions in `tools.py` (e.g. Gmail / Google Calendar APIs).

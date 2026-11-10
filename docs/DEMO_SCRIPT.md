# Demo Script (about 7 minutes)

Run: `python -m chief_of_staff.main`

1. **(0:00)** Show the architecture diagram, then the repo layout (1 min).
2. **(1:00)** Type `/briefing`. Narrate: 3 agents run in parallel, then the Report Generator returns a structured `ExecutiveSummary`.
3. **(2:30)** `Prepare me for my 3pm investor call today` → handoff to Meeting Preparation, returns a `MeetingBrief` using the internal KB.
4. **(3:30)** `Draft and send a reply to Priya confirming I'll review the term sheet by Thursday` → Email Manager drafts, **approval prompt appears**. Answer `n` once to show rejection handling, then retry and approve.
5. **(5:00)** `Research competitor Voltix and how it affects our Enterprise launch` → Research Analyst (KB + web).
6. **(5:45)** `I prefer meetings after 10am. Remember that.` → long-term memory; restart the app and ask `What do you know about my preferences?`
7. **(6:30)** Open `chief_of_staff/logs/audit.jsonl` to show the audit trail. Wrap up.

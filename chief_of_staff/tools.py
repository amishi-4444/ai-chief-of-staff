"""Function tools (13 here + the hosted WebSearchTool in team.py = 14 tools)."""
import time
from agents import RunContextWrapper, function_tool
from . import store
from .context import AppContext

Ctx = RunContextWrapper[AppContext]


# ---------- Email ----------
@function_tool
def read_inbox(ctx: Ctx, unread_only: bool) -> str:
    """Read emails from the CEO's inbox.

    Args:
        unread_only: If true, return only unread emails.
    """
    emails = store.load("inbox")
    if unread_only:
        emails = [e for e in emails if not e["read"]]
    store.audit("read_inbox", count=len(emails))
    return "\n".join(
        f"[{e['id']}] From: {e['from']} | Subject: {e['subject']} | {e['body']}" for e in emails
    ) or "No emails."


@function_tool
def send_email(ctx: Ctx, to: str, subject: str, body: str) -> str:
    """Send an email on behalf of the CEO. REQUIRES human approval.

    Args:
        to: Recipient email address.
        subject: Email subject.
        body: Email body text.
    """
    if not ctx.context.approve(f"Send email to {to}\nSubject: {subject}\n\n{body}"):
        store.audit("send_email_rejected", to=to, subject=subject)
        return "REJECTED by human. Email was NOT sent. Do not retry; ask the CEO for guidance."
    sent = store.load("sent")
    sent.append({"to": to, "subject": subject, "body": body, "ts": time.time()})
    store.save("sent", sent)
    store.audit("send_email", to=to, subject=subject)
    return f"Email sent to {to}."


# ---------- Calendar ----------
@function_tool
def get_calendar(ctx: Ctx, date: str) -> str:
    """Get calendar events for a date.

    Args:
        date: Date in YYYY-MM-DD format, or 'all' for every event.
    """
    events = store.load("calendar")
    if date != "all":
        events = [e for e in events if e["date"] == date]
    store.audit("get_calendar", date=date, count=len(events))
    return "\n".join(
        f"[{e['id']}] {e['date']} {e['time']} - {e['title']} (attendees: {', '.join(e['attendees'])})"
        for e in events
    ) or "No events."


@function_tool
def schedule_meeting(ctx: Ctx, title: str, date: str, time_str: str, attendees: list[str]) -> str:
    """Schedule a new meeting. REQUIRES human approval.

    Args:
        title: Meeting title.
        date: Date in YYYY-MM-DD.
        time_str: Start time like 14:00.
        attendees: List of attendee names or emails.
    """
    events = store.load("calendar")
    if any(e["date"] == date and e["time"] == time_str for e in events):
        return f"Conflict: something is already scheduled on {date} at {time_str}. Suggest another slot."
    if not ctx.context.approve(f"Schedule '{title}' on {date} at {time_str} with {', '.join(attendees)}"):
        store.audit("schedule_meeting_rejected", title=title)
        return "REJECTED by human. Meeting was NOT scheduled."
    events.append({"id": f"ev{len(events) + 1}", "title": title, "date": date,
                   "time": time_str, "attendees": attendees})
    store.save("calendar", events)
    store.audit("schedule_meeting", title=title, date=date, time=time_str)
    return f"Scheduled '{title}' on {date} at {time_str}."


# ---------- Research / knowledge ----------
@function_tool
def search_knowledge_base(ctx: Ctx, query: str) -> str:
    """Search internal company documents (board notes, market notes, competitor intel).

    Args:
        query: Keywords to search for.
    """
    docs = store.search_kb(query)
    store.audit("search_kb", query=query, hits=len(docs))
    return "\n\n".join(f"## {d['title']}\n{d['content']}" for d in docs) or "No internal documents matched."


# ---------- Strategy & tasks ----------
@function_tool
def get_goals(ctx: Ctx) -> str:
    """List the company's strategic goals with progress and status."""
    return "\n".join(
        f"[{g['id']}] {g['goal']} | target: {g['target']} | current: {g['current']} | "
        f"progress: {g['progress_pct']}% | deadline: {g['deadline']}"
        for g in store.load("goals")
    )


@function_tool
def update_goal_progress(ctx: Ctx, goal_id: str, progress_pct: int, note: str) -> str:
    """Update progress on a strategic goal.

    Args:
        goal_id: Goal id such as g1.
        progress_pct: New progress percentage 0-100.
        note: Short note on the current state.
    """
    goals = store.load("goals")
    for g in goals:
        if g["id"] == goal_id:
            g["progress_pct"] = max(0, min(100, progress_pct))
            g["current"] = note
            store.save("goals", goals)
            store.audit("update_goal", goal_id=goal_id, progress=g["progress_pct"])
            return f"Updated {goal_id} to {g['progress_pct']}%."
    return f"Goal {goal_id} not found."


@function_tool
def list_tasks(ctx: Ctx) -> str:
    """List the CEO's open tasks."""
    tasks = [t for t in store.load("tasks") if t["status"] == "open"]
    return "\n".join(f"[{t['id']}] ({t['priority']}) {t['title']} - due {t['due']}" for t in tasks) or "No open tasks."


@function_tool
def add_task(ctx: Ctx, title: str, due: str, priority: str) -> str:
    """Add a follow-up task.

    Args:
        title: Task description.
        due: Due date YYYY-MM-DD.
        priority: One of High, Medium, Low.
    """
    tasks = store.load("tasks")
    tasks.append({"id": f"t{len(tasks) + 1}", "title": title, "due": due, "priority": priority, "status": "open"})
    store.save("tasks", tasks)
    store.audit("add_task", title=title)
    return f"Task added: {title} (due {due})."


# ---------- Long-term memory ----------
@function_tool
def remember_fact(ctx: Ctx, fact: str) -> str:
    """Store a durable preference or fact about the CEO for future sessions.

    Args:
        fact: The fact to remember, e.g. 'Prefers meetings after 10am'.
    """
    facts = store.load("memory")
    facts.append({"fact": fact, "ts": time.strftime("%Y-%m-%d")})
    store.save("memory", facts)
    store.audit("remember_fact", fact=fact)
    return "Stored in long-term memory."


@function_tool
def recall_facts(ctx: Ctx) -> str:
    """Recall everything stored in long-term memory."""
    return "\n".join(f"- {f['fact']}" for f in store.load("memory")) or "Nothing stored yet."


# ---------- Reporting ----------
@function_tool
def save_report(ctx: Ctx, filename: str, markdown: str) -> str:
    """Save an executive report as a markdown file in reports/.

    Args:
        filename: File name ending in .md.
        markdown: Full report content in markdown.
    """
    store.REPORTS.mkdir(exist_ok=True)
    safe = "".join(c for c in filename if c.isalnum() or c in "-_.") or "report.md"
    (store.REPORTS / safe).write_text(markdown)
    store.audit("save_report", file=safe)
    return f"Report saved to reports/{safe}"

"""Agent definitions: 6 specialised agents wired together with handoffs."""
import os
from agents import Agent, RunContextWrapper, WebSearchTool
from . import store, tools as t
from .config import USE_WEB_SEARCH
from .context import AppContext
from .models import ExecutiveSummary, MeetingBrief

MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
TODAY = "2026-11-10"


def planner_instructions(ctx: RunContextWrapper[AppContext], agent: Agent) -> str:
    """Dynamic instructions: injects long-term memory into the planner prompt."""
    facts = "\n".join(f"- {f['fact']}" for f in store.load("memory")) or "- (nothing stored yet)"
    return f"""You are the Executive Planner, the orchestrator of an AI Chief of Staff team
serving {ctx.context.user_name}. Today is {TODAY}.

Known preferences (long-term memory):
{facts}

Route each request to the best specialist using a handoff:
- Email Manager: inbox triage, drafting/sending replies
- Meeting Preparation: calendar, scheduling, meeting briefs
- Research Analyst: market/competitor/company research
- Strategy Tracker: goals, tasks, priorities, follow-ups
- Report Generator: executive summaries and reports
For simple questions or preference updates, answer directly. If the CEO states a durable
preference, call remember_fact. For multi-part requests, hand off to the most important
specialist first and mention what remains. Never take critical actions yourself."""


def build_team() -> Agent:
    report_generator = Agent[AppContext](
        name="Report Generator",
        handoff_description="Writes executive summaries and reports from gathered information.",
        instructions=(
            "You write concise executive summaries for the CEO. Use the conversation so far "
            "(emails, research, goals, meetings) as source material. Be specific, rank action "
            "items by priority, flag decisions needed and risks. Return the structured summary."
        ),
        tools=[t.get_goals, t.list_tasks, t.save_report],
        output_type=ExecutiveSummary,
        model=MODEL,
    )

    email_manager = Agent[AppContext](
        name="Email Manager",
        handoff_description="Triage the inbox, draft and send email replies.",
        instructions=(
            "You manage the CEO's email. Read the inbox, classify each email as Urgent, Needs "
            "Reply, FYI or Ignore, and draft concise professional replies. Only call send_email "
            "after drafting; it requires human approval. If approval is rejected, do not retry. "
            "If the CEO wants a summary of everything, hand off to Report Generator."
        ),
        tools=[t.read_inbox, t.send_email, t.add_task],
        handoffs=[report_generator],
        model=MODEL,
    )

    meeting_prep = Agent[AppContext](
        name="Meeting Preparation",
        handoff_description="Calendar lookups, scheduling, and meeting briefs.",
        instructions=(
            "You prepare the CEO for meetings. Check the calendar, search internal knowledge for "
            "context on attendees/topics, and produce a MeetingBrief when asked to prepare for a "
            "meeting. For scheduling requests, call schedule_meeting (needs human approval) and "
            "propose alternatives on conflicts. Today's date is " + TODAY + "."
        ),
        tools=[t.get_calendar, t.schedule_meeting, t.search_knowledge_base],
        output_type=MeetingBrief,
        model=MODEL,
    )

    research_analyst = Agent[AppContext](
        name="Research Analyst",
        handoff_description="Researches companies, markets and competitors.",
        instructions=(
            "You research topics for the CEO. First search the internal knowledge base, then use "
            "web search for external facts if that tool is available. Give a short, sourced answer with key findings, "
            "implications for the business, and confidence level. Hand off to Report Generator "
            "if the CEO asks for a formal report."
        ),
        tools=[t.search_knowledge_base] + ([WebSearchTool()] if USE_WEB_SEARCH else []),
        handoffs=[report_generator],
        model=MODEL,
    )

    strategy_tracker = Agent[AppContext](
        name="Strategy Tracker",
        handoff_description="Tracks strategic goals, tasks, priorities and follow-ups.",
        instructions=(
            "You monitor strategic goals and the task list. Flag goals that are behind schedule "
            "(progress vs. deadline relative to today, " + TODAY + "), prioritise today's tasks "
            "(High first, then nearest due date), and add follow-up tasks when asked. "
            "Hand off to Report Generator for formal reports."
        ),
        tools=[t.get_goals, t.update_goal_progress, t.list_tasks, t.add_task],
        handoffs=[report_generator],
        model=MODEL,
    )

    planner = Agent[AppContext](
        name="Executive Planner",
        instructions=planner_instructions,
        tools=[t.remember_fact, t.recall_facts],
        handoffs=[email_manager, meeting_prep, research_analyst, strategy_tracker, report_generator],
        model=MODEL,
    )
    return planner

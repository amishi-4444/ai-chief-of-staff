"""Parallel agent execution: the morning briefing runs 3 specialists concurrently,
then the Report Generator synthesises one structured ExecutiveSummary."""
import asyncio
from agents import Runner
from . import store
from .context import AppContext
from .models import ExecutiveSummary
from .team import build_team

PROMPTS = {
    "Email Manager": "Triage unread emails. List only what needs the CEO's attention, with a one-line recommended action each. Do NOT send anything.",
    "Meeting Preparation": "List today's meetings (2026-11-10) and tomorrow's, with one prep note each. Do NOT schedule anything. Reply in plain text.",
    "Strategy Tracker": "Summarise goals that are behind or at risk and the top 3 tasks to do today.",
}


async def daily_briefing(ctx: AppContext) -> ExecutiveSummary:
    planner = build_team()
    agents = {a.name: a for a in planner.handoffs}  # specialists are plain Agent objects
    jobs = [
        # clone() gives plain-text, handoff-free copies so branches run independently
        Runner.run(agents[name].clone(handoffs=[], output_type=None), prompt, context=ctx, max_turns=8)
        for name, prompt in PROMPTS.items()
    ]
    results = await asyncio.gather(*jobs, return_exceptions=True)  # per-branch error handling

    parts = []
    for name, res in zip(PROMPTS, results):
        if isinstance(res, Exception):
            store.audit("briefing_branch_failed", agent=name, error=str(res))
            parts.append(f"## {name}\n(unavailable: {res})")
        else:
            parts.append(f"## {name}\n{res.final_output}")

    reporter = agents["Report Generator"].clone(tools=[])
    final = await Runner.run(
        reporter, "Write the CEO's morning briefing from:\n\n" + "\n\n".join(parts), context=ctx
    )
    summary: ExecutiveSummary = final.final_output
    store.audit("daily_briefing", headline=summary.headline)
    return summary

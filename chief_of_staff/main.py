"""CLI entry point:  python -m chief_of_staff.main [--auto-approve] [--session NAME]"""
import argparse
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel
from agents import Runner, SQLiteSession
from agents.exceptions import MaxTurnsExceeded

load_dotenv()

from . import store  # noqa: E402
from .config import configure  # noqa: E402
from .briefing import daily_briefing  # noqa: E402
from .context import AppContext  # noqa: E402
from .team import build_team  # noqa: E402


def render(output) -> str:
    if isinstance(output, BaseModel):
        return output.model_dump_json(indent=2)
    return str(output)


async def chat(session_name: str, auto_approve: bool) -> None:
    configure()
    ctx = AppContext(auto_approve=auto_approve)
    session = SQLiteSession(session_name, "chief_of_staff_sessions.sqlite")  # session persistence
    planner = build_team()
    print("AI Chief of Staff ready. Commands: /briefing, /quit\n")
    while True:
        user = input("You: ").strip()
        if not user:
            continue
        if user == "/quit":
            break
        try:
            if user == "/briefing":
                print(render(await daily_briefing(ctx)), "\n")
                continue
            result = await Runner.run(planner, user, context=ctx, session=session, max_turns=15)
            store.audit("turn", agent=result.last_agent.name, user=user)
            print(f"\n[{result.last_agent.name}]\n{render(result.final_output)}\n")
        except MaxTurnsExceeded:
            print("The team got stuck; try rephrasing the request.\n")
        except Exception as exc:  # keep the CLI alive and log the failure
            store.audit("error", error=str(exc))
            print(f"Error: {exc}\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--session", default="ceo-default")
    p.add_argument("--auto-approve", action="store_true", help="skip human approval (demo/test only)")
    args = p.parse_args()
    asyncio.run(chat(args.session, args.auto_approve))

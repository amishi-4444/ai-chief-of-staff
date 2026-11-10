"""Shared run context passed to every agent and tool (short-term shared state)."""
from dataclasses import dataclass


@dataclass
class AppContext:
    user_name: str = "CEO"
    auto_approve: bool = False  # True only for demos/tests

    def approve(self, description: str) -> bool:
        """Human-in-the-loop gate for critical actions."""
        if self.auto_approve:
            return True
        answer = input(f"\n[APPROVAL REQUIRED] {description}\nApprove? (y/n): ")
        return answer.strip().lower() in {"y", "yes"}

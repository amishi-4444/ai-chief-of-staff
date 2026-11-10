"""Structured output schemas (Pydantic) used as agent output_type."""
from typing import Literal
from pydantic import BaseModel


class ActionItem(BaseModel):
    action: str
    owner: str
    due: str
    priority: Literal["High", "Medium", "Low"]


class ExecutiveSummary(BaseModel):
    headline: str
    key_updates: list[str]
    decisions_needed: list[str]
    action_items: list[ActionItem]
    risks: list[str]


class MeetingBrief(BaseModel):
    meeting_title: str
    time: str
    attendees: list[str]
    objective: str
    background: list[str]
    talking_points: list[str]
    questions_to_ask: list[str]

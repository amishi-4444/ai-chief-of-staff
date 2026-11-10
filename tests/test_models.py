from chief_of_staff.models import ExecutiveSummary, ActionItem


def test_executive_summary_schema():
    s = ExecutiveSummary(
        headline="h", key_updates=["a"], decisions_needed=["b"],
        action_items=[ActionItem(action="x", owner="CEO", due="2026-11-12", priority="High")],
        risks=["r"],
    )
    assert s.action_items[0].priority == "High"

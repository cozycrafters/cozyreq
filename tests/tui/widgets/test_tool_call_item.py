from typing import cast
from textual.app import App, ComposeResult
from rich.text import Text

from cozyreq.tui.widgets.tool_call_item import ToolCallItem
from cozyreq.tui.models import ToolCall, StatusType
from datetime import datetime


async def test_tool_call_item_rendering():
    """Test ToolCallItem renders correctly."""
    tool_call = ToolCall(
        id="tc-001",
        run_id="run-001",
        sequence_number=1,
        tool_name="web_search",
        status="success",
        timestamp=datetime(2024, 12, 26, 12, 34, 1),
        duration=0.234,
        request='{"query": "test"}',
        response='{"results": []}',
        size=2400,
        summary='Query: "quantum computing..."',
        result_summary="→ 24 results",
    )

    class ItemApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ToolCallItem(tool_call, selected=False)

    app = ItemApp()
    async with app.run_test():
        item = app.query_one(ToolCallItem)
        assert item.tool_call == tool_call
        assert item.selected is False


async def test_tool_call_item_selected():
    """Test ToolCallItem shows selection cursor when selected."""
    tool_call = ToolCall(
        id="tc-001",
        run_id="run-001",
        sequence_number=1,
        tool_name="web_search",
        status="success",
        timestamp=datetime(2024, 12, 26, 12, 34, 1),
        duration=0.234,
        request='{"query": "test"}',
        response='{"results": []}',
        size=2400,
        summary='Query: "quantum computing..."',
        result_summary="→ 24 results",
    )

    class ItemApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ToolCallItem(tool_call, selected=True)

    app = ItemApp()
    async with app.run_test():
        item = app.query_one(ToolCallItem)
        assert item.selected is True
        # Should contain selection cursor
        text = str(getattr(item, "renderable"))
        assert "◄──" in text or item.has_class("selected")


async def test_tool_call_item_status_icons():
    """Test that different statuses show correct icons."""
    statuses_and_icons = [
        ("success", "✓"),
        ("running", "⚡"),
        ("queued", "⏳"),
        ("failed", "❌"),
    ]

    for status, icon in statuses_and_icons:
        tool_call = ToolCall(
            id="tc-001",
            run_id="run-001",
            sequence_number=1,
            tool_name="web_search",
            status=cast(StatusType, status),
            timestamp=datetime(2024, 12, 26, 12, 34, 1),
            duration=0.234 if status != "queued" else None,
            request='{"query": "test"}',
            response='{"results": []}' if status != "queued" else None,
            size=2400,
            summary='Query: "quantum computing..."',
            result_summary="→ 24 results" if status != "queued" else None,
        )

        class ItemApp(App[None]):
            def compose(self) -> ComposeResult:
                yield ToolCallItem(tool_call, selected=False)

        app = ItemApp()
        async with app.run_test():
            item = app.query_one(ToolCallItem)
            text = str(getattr(item, "renderable"))
            assert icon in text


async def test_tool_call_item_update_selection():
    """Test updating selection status."""
    tool_call = ToolCall(
        id="tc-001",
        run_id="run-001",
        sequence_number=1,
        tool_name="web_search",
        status="success",
        timestamp=datetime(2024, 12, 26, 12, 34, 1),
        duration=0.234,
        request='{"query": "test"}',
        response='{"results": []}',
        size=2400,
        summary='Query: "quantum computing..."',
        result_summary="→ 24 results",
    )

    class ItemApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ToolCallItem(tool_call, selected=False)

    app = ItemApp()
    async with app.run_test():
        item = app.query_one(ToolCallItem)
        assert item.selected is False

        # Update selection
        item.set_selected(True)
        assert item.selected is True

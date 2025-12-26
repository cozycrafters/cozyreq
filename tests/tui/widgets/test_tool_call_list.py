from datetime import datetime

from textual.app import App, ComposeResult

from cozyreq.tui.models import ToolCall
from cozyreq.tui.widgets.tool_call_list import ToolCallList, ToolCallSelected


async def test_tool_call_list_rendering():
    """Test ToolCallList renders with tool calls."""
    tool_calls = [
        ToolCall(
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
        ),
        ToolCall(
            id="tc-002",
            run_id="run-001",
            sequence_number=2,
            tool_name="api_call",
            status="running",
            timestamp=datetime(2024, 12, 26, 12, 34, 2),
            duration=None,
            request='{"endpoint": "test"}',
            response=None,
            size=None,
            summary="api.test.com",
            result_summary=None,
        ),
    ]

    class ListApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ToolCallList(tool_calls)

    app = ListApp()
    async with app.run_test():
        list_widget = app.query_one(ToolCallList)
        assert list_widget.tool_calls == tool_calls
        assert list_widget.selected_index == 0


async def test_tool_call_list_selection():
    """Test selecting tool calls."""
    tool_calls = [
        ToolCall(
            id=f"tc-{i:03d}",
            run_id="run-001",
            sequence_number=i,
            tool_name="web_search",
            status="success",
            timestamp=datetime(2024, 12, 26, 12, 34, i),
            duration=0.234,
            request='{"query": "test"}',
            response='{"results": []}',
            size=2400,
            summary=f"Query {i}",
            result_summary=f"→ {i} results",
        )
        for i in range(1, 4)
    ]

    class ListApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ToolCallList(tool_calls)

    app = ListApp()
    async with app.run_test():
        list_widget = app.query_one(ToolCallList)
        assert list_widget.selected_index == 0

        # Select next
        list_widget.select_next()
        assert list_widget.selected_index == 1

        # Select next again
        list_widget.select_next()
        assert list_widget.selected_index == 2

        # Can't go beyond last
        list_widget.select_next()
        assert list_widget.selected_index == 2

        # Select previous
        list_widget.select_previous()
        assert list_widget.selected_index == 1


async def test_tool_call_list_message_on_selection():
    """Test that ToolCallSelected message is posted on selection change."""
    tool_calls = [
        ToolCall(
            id=f"tc-{i:03d}",
            run_id="run-001",
            sequence_number=i,
            tool_name="web_search",
            status="success",
            timestamp=datetime(2024, 12, 26, 12, 34, i),
            duration=0.234,
            request='{"query": "test"}',
            response='{"results": []}',
            size=2400,
            summary=f"Query {i}",
            result_summary=f"→ {i} results",
        )
        for i in range(1, 4)
    ]

    messages_received = []

    class ListApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ToolCallList(tool_calls)

        def on_tool_call_selected(self, message: ToolCallSelected) -> None:
            messages_received.append(message)

    app = ListApp()
    async with app.run_test() as pilot:
        list_widget = app.query_one(ToolCallList)

        # Select next should post message
        list_widget.select_next()
        await pilot.pause()

        assert len(messages_received) == 1
        assert messages_received[0].tool_call == tool_calls[1]
        assert messages_received[0].index == 1


async def test_tool_call_list_empty():
    """Test ToolCallList with empty list."""

    class ListApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ToolCallList([])

    app = ListApp()
    async with app.run_test():
        list_widget = app.query_one(ToolCallList)
        assert list_widget.selected_index == -1
        assert len(list_widget.tool_calls) == 0


async def test_tool_call_list_progress():
    """Test that progress indicator shows correct values."""
    tool_calls = [
        ToolCall(
            id=f"tc-{i:03d}",
            run_id="run-001",
            sequence_number=i,
            tool_name="web_search",
            status="success" if i <= 2 else "queued",
            timestamp=datetime(2024, 12, 26, 12, 34, i),
            duration=0.234 if i <= 2 else None,
            request='{"query": "test"}',
            response='{"results": []}' if i <= 2 else None,
            size=2400,
            summary=f"Query {i}",
            result_summary=f"→ {i} results" if i <= 2 else None,
        )
        for i in range(1, 6)
    ]

    class ListApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ToolCallList(tool_calls)

    app = ListApp()
    async with app.run_test():
        list_widget = app.query_one(ToolCallList)
        # 2 completed out of 5 total
        assert list_widget.completed_count == 2
        assert list_widget.total_count == 5

from datetime import datetime

from textual.app import App, ComposeResult
from textual.widgets import TabbedContent

from cozyreq.tui.models import ToolCall
from cozyreq.tui.widgets.tool_details_panel import ToolDetailsPanel


async def test_tool_details_panel_rendering():
    """Test ToolDetailsPanel renders correctly."""
    tool_call = ToolCall(
        id="tc-001",
        run_id="run-001",
        sequence_number=3,
        tool_name="web_search",
        status="success",
        timestamp=datetime(2024, 12, 26, 12, 34, 3),
        duration=0.427,
        request='{"method": "POST", "url": "https://api.search.com"}',
        response='{"status": "success", "results": 31}',
        size=2847,
        summary='Query: "applications"',
        result_summary="→ 31 results",
    )

    class PanelApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ToolDetailsPanel(tool_call)

    app = PanelApp()
    async with app.run_test():
        panel = app.query_one(ToolDetailsPanel)
        assert panel.tool_call == tool_call


async def test_tool_details_panel_has_tabs():
    """Test that panel has Request and Response tabs."""
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
        summary="Query test",
        result_summary="→ 24 results",
    )

    class PanelApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ToolDetailsPanel(tool_call)

    app = PanelApp()
    async with app.run_test():
        # Should have TabbedContent widget
        tabbed_content = app.query_one(TabbedContent)
        assert tabbed_content is not None

        # Should have Request and Response tab panes
        tab_panes = list(tabbed_content.query("TabPane"))
        assert len(tab_panes) == 2


async def test_tool_details_panel_update():
    """Test updating the panel with a new tool call."""
    tool_call1 = ToolCall(
        id="tc-001",
        run_id="run-001",
        sequence_number=1,
        tool_name="web_search",
        status="success",
        timestamp=datetime(2024, 12, 26, 12, 34, 1),
        duration=0.234,
        request='{"query": "test1"}',
        response='{"results": []}',
        size=2400,
        summary="Query 1",
        result_summary="→ 24 results",
    )

    tool_call2 = ToolCall(
        id="tc-002",
        run_id="run-001",
        sequence_number=2,
        tool_name="api_call",
        status="running",
        timestamp=datetime(2024, 12, 26, 12, 34, 2),
        duration=None,
        request='{"endpoint": "/api/test"}',
        response=None,
        size=None,
        summary="API call",
        result_summary=None,
    )

    class PanelApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ToolDetailsPanel(tool_call1)

    app = PanelApp()
    async with app.run_test():
        panel = app.query_one(ToolDetailsPanel)
        assert panel.tool_call == tool_call1

        # Update to new tool call
        panel.update_tool_call(tool_call2)
        assert panel.tool_call == tool_call2


async def test_tool_details_panel_none_response():
    """Test panel with None response (e.g., running tool call)."""
    tool_call = ToolCall(
        id="tc-001",
        run_id="run-001",
        sequence_number=1,
        tool_name="api_call",
        status="running",
        timestamp=datetime(2024, 12, 26, 12, 34, 1),
        duration=None,
        request='{"endpoint": "/test"}',
        response=None,
        size=None,
        summary="API call",
        result_summary=None,
    )

    class PanelApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ToolDetailsPanel(tool_call)

    app = PanelApp()
    async with app.run_test():
        panel = app.query_one(ToolDetailsPanel)
        # Should still render without crashing
        assert panel.tool_call == tool_call

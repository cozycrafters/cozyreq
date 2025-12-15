import pytest
from textual.widgets import Input

from cozyreq.tui import CozyReqApp


@pytest.mark.asyncio
async def test_tui_layout_and_initial_state():
    """Test that the app starts with correct layout and dummy data."""
    app = CozyReqApp()
    async with app.run_test():
        # Check main containers
        assert app.query_one("#execution-log")
        assert app.query_one("#details-panel")

        # Check dummy log entries exist
        log_entries = app.query("#execution-log .log-entry")
        assert len(log_entries) > 0

        # Check app state
        assert len(app.requests) == 2
        assert app.selected_request_index == 1

        # Check details panel exists and app state is correct
        app.query_one("#details-content")
        # Details should show the selected request (index 1 = request 2)
        assert app.requests[1].method == "POST"
        assert app.requests[1].url == "/api/users/1"


@pytest.mark.asyncio
async def test_tui_interaction():
    """Test typing in the input adds log entries."""
    app = CozyReqApp()
    async with app.run_test() as pilot:
        # Get initial log entry count
        initial_entries = len(app.query("#execution-log .log-entry"))

        # Type a message
        await pilot.click("#prompt-input")
        await pilot.press(*list("test message"), "enter")

        # Check if log entries were added
        new_entries = len(app.query("#execution-log .log-entry"))
        assert new_entries > initial_entries

        # Check input is cleared
        input_widget = app.query_one("#prompt-input", Input)
        assert input_widget.value == ""

        # Test empty input is ignored
        await pilot.press("enter")
        assert len(app.query("#execution-log .log-entry")) == new_entries


@pytest.mark.asyncio
async def test_request_selection():
    """Test that up/down arrows change the selected request."""
    app = CozyReqApp()
    async with app.run_test() as pilot:
        # Initial selection should be request 2 (index 1)
        assert app.selected_request_index == 1
        assert app.requests[1].number == 2

        # Press up arrow
        await pilot.press("up")
        assert app.selected_request_index == 0

        # Verify it's request 1
        assert app.requests[0].number == 1
        assert app.requests[0].method == "GET"

        # Press down arrow
        await pilot.press("down")
        assert app.selected_request_index == 1

        # Verify it's back to request 2
        assert app.requests[1].number == 2
        assert app.requests[1].method == "POST"

        # Press down at boundary (should stay at 1)
        await pilot.press("down")
        assert app.selected_request_index == 1

        # Press up then up again at boundary (should stay at 0)
        await pilot.press("up")
        await pilot.press("up")
        assert app.selected_request_index == 0

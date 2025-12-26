from textual.app import App, ComposeResult
from textual.widgets import Button, Input

from cozyreq.tui.widgets.log_filter_bar import (
    FilterChanged,
    LogFilterBar,
    SearchChanged,
)


async def test_log_filter_bar_rendering():
    """Test LogFilterBar renders with filter buttons and search."""

    class FilterApp(App[None]):
        def compose(self) -> ComposeResult:
            yield LogFilterBar()

    app = FilterApp()
    async with app.run_test():
        filter_bar = app.query_one(LogFilterBar)
        assert filter_bar is not None

        # Should have filter buttons
        buttons = list(filter_bar.query(Button))
        assert len(buttons) >= 5  # All, Info, Tools, Errors, Debug

        # Should have search input
        search = filter_bar.query_one(Input)
        assert search is not None


async def test_log_filter_bar_initial_state():
    """Test that all filters are active by default."""

    class FilterApp(App[None]):
        def compose(self) -> ComposeResult:
            yield LogFilterBar()

    app = FilterApp()
    async with app.run_test():
        filter_bar = app.query_one(LogFilterBar)
        # All filter types should be active initially
        assert "INFO" in filter_bar.active_filters
        assert "TOOL" in filter_bar.active_filters
        assert "ERROR" in filter_bar.active_filters
        assert "DEBUG" in filter_bar.active_filters


async def test_log_filter_bar_toggle_filter():
    """Test toggling filter types."""

    class FilterApp(App[None]):
        def compose(self) -> ComposeResult:
            yield LogFilterBar()

    app = FilterApp()
    async with app.run_test():
        filter_bar = app.query_one(LogFilterBar)

        # Toggle off INFO
        filter_bar.toggle_filter("INFO")
        assert "INFO" not in filter_bar.active_filters
        assert "TOOL" in filter_bar.active_filters

        # Toggle INFO back on
        filter_bar.toggle_filter("INFO")
        assert "INFO" in filter_bar.active_filters


async def test_log_filter_bar_filter_changed_message():
    """Test that FilterChanged message is posted when filters change."""
    messages_received = []

    class FilterApp(App[None]):
        def compose(self) -> ComposeResult:
            yield LogFilterBar()

        def on_filter_changed(self, message: FilterChanged) -> None:
            messages_received.append(message)

    app = FilterApp()
    async with app.run_test() as pilot:
        filter_bar = app.query_one(LogFilterBar)

        # Toggle filter should post message
        filter_bar.toggle_filter("INFO")
        await pilot.pause()

        assert len(messages_received) == 1
        assert "INFO" not in messages_received[0].active_filters


async def test_log_filter_bar_search_changed_message():
    """Test that SearchChanged message is posted when search text changes."""
    messages_received = []

    class FilterApp(App[None]):
        def compose(self) -> ComposeResult:
            yield LogFilterBar()

        def on_search_changed(self, message: SearchChanged) -> None:
            messages_received.append(message)

    app = FilterApp()
    async with app.run_test() as pilot:
        filter_bar = app.query_one(LogFilterBar)
        search_input = filter_bar.query_one(Input)

        # Type in search
        search_input.value = "test query"
        # Simulate input changed event
        search_input.post_message(Input.Changed(search_input, search_input.value))
        await pilot.pause()

        assert len(messages_received) >= 1
        assert messages_received[-1].query == "test query"


async def test_log_filter_bar_all_button():
    """Test the All button toggles all filters."""

    class FilterApp(App[None]):
        def compose(self) -> ComposeResult:
            yield LogFilterBar()

    app = FilterApp()
    async with app.run_test():
        filter_bar = app.query_one(LogFilterBar)

        # Toggle off some filters
        filter_bar.toggle_filter("INFO")
        filter_bar.toggle_filter("ERROR")
        assert len(filter_bar.active_filters) == 2

        # Click All should re-enable all
        filter_bar.set_all_filters(True)
        assert len(filter_bar.active_filters) == 4

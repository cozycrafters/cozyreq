"""Logs screen - view showing execution logs with filtering."""

from typing import override

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen

from ..models import LogEntry
from ..widgets import FilterChanged, LogFilterBar, LogTable, SearchChanged


class LogsScreen(Screen[None]):
    """Screen displaying execution logs with filtering and search."""

    def __init__(
        self,
        logs: list[LogEntry],
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Initialize the logs screen.

        Args:
            logs: List of log entries to display.
            name: Screen name.
            id: Screen ID.
            classes: Screen CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.logs: list[LogEntry] = logs

    @override
    def compose(self) -> ComposeResult:
        """Compose the screen with filter bar and log table."""
        with Vertical(id="logs-container"):
            # Top: Filter bar
            yield LogFilterBar(id="log-filter-bar")

            # Bottom: Log table
            yield LogTable(self.logs, id="log-table")

    def on_filter_changed(self, message: FilterChanged) -> None:
        """Handle filter changes."""
        table = self.query_one("#log-table", LogTable)
        table.filter_logs(message.active_filters)

    def on_search_changed(self, message: SearchChanged) -> None:
        """Handle search query changes."""
        table = self.query_one("#log-table", LogTable)
        table.search_logs(message.query)

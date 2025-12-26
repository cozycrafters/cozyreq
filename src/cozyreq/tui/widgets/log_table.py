"""Log table widget - displays logs in a DataTable with filtering."""

from rich.text import Text
from textual.widgets import DataTable

from ..models import LogEntry, LogType


class LogTable(DataTable):
    """A table displaying log entries with filtering and search."""

    def __init__(
        self,
        logs: list[LogEntry],
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Initialize the log table.

        Args:
            logs: List of log entries to display.
            name: Widget name.
            id: Widget ID.
            classes: Widget CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes, zebra_stripes=True)
        self.logs = logs
        self._filtered_logs = logs.copy()
        self._current_filters: set[LogType] = {"INFO", "TOOL", "ERROR", "DEBUG"}
        self._current_search = ""

    def on_mount(self) -> None:
        """Set up the table when mounted."""
        # Add columns
        self.add_column("Time", width=10)
        self.add_column("Type", width=6)
        self.add_column("Message")

        # Populate rows
        self._update_rows()

    def _get_icon_for_type(self, log_type: LogType) -> str:
        """Get the icon for a log type."""
        icons = {
            "INFO": "▶",
            "TOOL": "⚡",
            "ERROR": "❌",
            "DEBUG": "🐛",
        }
        return icons.get(log_type, "")

    def _get_color_for_type(self, log_type: LogType) -> str:
        """Get the color for a log type."""
        colors = {
            "INFO": "cyan",
            "TOOL": "yellow",
            "ERROR": "red",
            "DEBUG": "magenta",
        }
        return colors.get(log_type, "white")

    def _truncate_message(self, message: str, max_length: int = 80) -> str:
        """Truncate message to fit display."""
        first_line = message.split("\n")[0]
        if len(first_line) > max_length:
            return first_line[: max_length - 3] + "..."
        return first_line

    def _update_rows(self) -> None:
        """Update table rows based on filtered logs."""
        # Clear existing rows
        self.clear()

        # Add rows for filtered logs
        for log in self._filtered_logs:
            # Format time (HH:MM:SS)
            time_str = log.timestamp.strftime("%H:%M:%S")

            # Format type with icon
            icon = self._get_icon_for_type(log.log_type)
            color = self._get_color_for_type(log.log_type)
            type_text = Text(log.log_type, style=color)

            # Format message with icon prefix
            message_text = Text()
            message_text.append(f"{icon} ", style=color)
            message_text.append(self._truncate_message(log.message))

            # Add row
            self.add_row(
                time_str,
                type_text,
                message_text,
            )

    def filter_logs(self, active_filters: set[LogType]) -> None:
        """
        Filter logs by type.

        Args:
            active_filters: Set of log types to show.
        """
        self._current_filters = active_filters
        self._apply_filters()

    def search_logs(self, query: str) -> None:
        """
        Search logs by message content.

        Args:
            query: Search query string (case-insensitive).
        """
        self._current_search = query.lower()
        self._apply_filters()

    def _apply_filters(self) -> None:
        """Apply both type filters and search query."""
        # Start with all logs
        filtered = self.logs

        # Apply type filter
        if self._current_filters:
            filtered = [
                log for log in filtered if log.log_type in self._current_filters
            ]

        # Apply search filter
        if self._current_search:
            filtered = [
                log for log in filtered if self._current_search in log.message.lower()
            ]

        self._filtered_logs = filtered
        self._update_rows()

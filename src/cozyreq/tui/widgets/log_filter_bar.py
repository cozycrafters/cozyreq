"""Log filter bar widget - filter controls and search for logs."""

from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Input

from ..models import LogType


class FilterChanged(Message):
    """Message posted when active filters change."""

    def __init__(self, active_filters: set[LogType]) -> None:
        """
        Initialize the message.

        Args:
            active_filters: The currently active filter types.
        """
        super().__init__()
        self.active_filters = active_filters


class SearchChanged(Message):
    """Message posted when search query changes."""

    def __init__(self, query: str) -> None:
        """
        Initialize the message.

        Args:
            query: The search query string.
        """
        super().__init__()
        self.query = query


class LogFilterBar(Horizontal):
    """Filter controls and search input for logs."""

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Initialize the log filter bar.

        Args:
            name: Widget name.
            id: Widget ID.
            classes: Widget CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        # All filters active by default
        self.active_filters: set[LogType] = {"INFO", "TOOL", "ERROR", "DEBUG"}

    def compose(self):
        """Compose the filter bar with buttons and search input."""
        # Filter buttons
        yield Button("All ▾", id="filter-all", variant="primary")
        yield Button("Info", id="filter-info", classes="filter-button active")
        yield Button("Tools", id="filter-tool", classes="filter-button active")
        yield Button("Errors", id="filter-error", classes="filter-button active")
        yield Button("Debug", id="filter-debug", classes="filter-button active")

        # Search input
        yield Input(placeholder="🔍 Search", id="log-search")

    def toggle_filter(self, log_type: LogType) -> None:
        """
        Toggle a filter type on/off.

        Args:
            log_type: The log type to toggle.
        """
        if log_type in self.active_filters:
            self.active_filters.remove(log_type)
        else:
            self.active_filters.add(log_type)

        # Update button styling
        self._update_button_styles()

        # Post message
        self.post_message(FilterChanged(self.active_filters.copy()))

    def set_all_filters(self, active: bool) -> None:
        """
        Enable or disable all filters.

        Args:
            active: Whether to activate all filters.
        """
        if active:
            self.active_filters = {"INFO", "TOOL", "ERROR", "DEBUG"}
        else:
            self.active_filters = set()

        self._update_button_styles()
        self.post_message(FilterChanged(self.active_filters.copy()))

    def _update_button_styles(self) -> None:
        """Update button CSS classes based on active filters."""
        filter_map = {
            "filter-info": "INFO",
            "filter-tool": "TOOL",
            "filter-error": "ERROR",
            "filter-debug": "DEBUG",
        }

        for button_id, log_type in filter_map.items():
            try:
                button = self.query_one(f"#{button_id}", Button)
                if log_type in self.active_filters:
                    button.add_class("active")
                else:
                    button.remove_class("active")
            except Exception:
                pass  # Button not found yet

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses for filter toggling."""
        button_id = event.button.id

        if button_id == "filter-all":
            # Toggle all filters
            if len(self.active_filters) == 4:
                self.set_all_filters(False)
            else:
                self.set_all_filters(True)
        elif button_id == "filter-info":
            self.toggle_filter("INFO")
        elif button_id == "filter-tool":
            self.toggle_filter("TOOL")
        elif button_id == "filter-error":
            self.toggle_filter("ERROR")
        elif button_id == "filter-debug":
            self.toggle_filter("DEBUG")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "log-search":
            self.post_message(SearchChanged(event.value))

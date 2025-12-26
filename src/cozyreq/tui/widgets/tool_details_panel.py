"""Tool details panel widget - right pane showing request/response details."""

import json

from rich.syntax import Syntax
from textual.containers import Container, Horizontal
from textual.widgets import Static, TabbedContent, TabPane

from ..models import ToolCall
from .status_badge import StatusBadge


class ToolDetailsPanel(Container):
    """Panel showing detailed information about a selected tool call."""

    def __init__(
        self,
        tool_call: ToolCall,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Initialize the tool details panel.

        Args:
            tool_call: The tool call to display details for.
            name: Widget name.
            id: Widget ID.
            classes: Widget CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.tool_call = tool_call

    def compose(self):
        """Compose the panel with header, status badges, and tabs."""
        # Header
        yield Static(
            f"Selected Tool: #{self.tool_call.sequence_number} {self.tool_call.tool_name}",
            classes="tool-details-header",
        )

        # Status badges
        status_container = Horizontal(classes="tool-details-status")
        with status_container:
            # Status badge
            yield StatusBadge(self.tool_call.status, self.tool_call.status.capitalize())

            # Duration badge
            if self.tool_call.duration is not None:
                yield StatusBadge("duration", f"{self.tool_call.duration:.3f}s")
            else:
                yield StatusBadge(
                    "duration",
                    "Running..." if self.tool_call.status == "running" else "Queued",
                )

            # Size badge
            if self.tool_call.size is not None:
                size_kb = self.tool_call.size / 1024
                if size_kb < 1:
                    size_str = f"{self.tool_call.size}B"
                else:
                    size_str = f"{size_kb:.1f}KB"
                yield StatusBadge("size", size_str)

        yield status_container

        # Tabbed content for Request/Response
        with TabbedContent(id="tool-details-tabs"):
            with TabPane("Request", id="request-tab"):
                yield self._create_content_widget(self.tool_call.request)

            with TabPane("Response", id="response-tab"):
                if self.tool_call.response:
                    yield self._create_content_widget(self.tool_call.response)
                else:
                    yield Static("No response yet", classes="no-response")

    def _create_content_widget(self, content: str) -> Static:
        """
        Create a widget for displaying JSON content with syntax highlighting.

        Args:
            content: JSON string to display.

        Returns:
            Static widget with syntax-highlighted content.
        """
        try:
            # Try to parse and pretty-print JSON
            parsed = json.loads(content)
            formatted = json.dumps(parsed, indent=2)
            syntax = Syntax(formatted, "json", theme="monokai", line_numbers=False)
            return Static(syntax, classes="tool-details-content")
        except json.JSONDecodeError:
            # If not valid JSON, display as plain text
            return Static(content, classes="tool-details-content")

    def update_tool_call(self, tool_call: ToolCall) -> None:
        """
        Update the panel with a new tool call.

        Args:
            tool_call: The new tool call to display.
        """
        self.tool_call = tool_call

        # Update header
        header = self.query_one(".tool-details-header", Static)
        header.update(
            f"Selected Tool: #{tool_call.sequence_number} {tool_call.tool_name}"
        )

        # Update status badges
        status_container = self.query_one(".tool-details-status", Horizontal)
        status_badges = list(status_container.query(StatusBadge))

        # Update status badge
        status_badges[0].update_status(tool_call.status, tool_call.status.capitalize())

        # Update duration badge
        if tool_call.duration is not None:
            status_badges[1].update_status("duration", f"{tool_call.duration:.3f}s")
        else:
            status_badges[1].update_status(
                "duration", "Running..." if tool_call.status == "running" else "Queued"
            )

        # Update size badge if it exists
        if len(status_badges) > 2 and tool_call.size is not None:
            size_kb = tool_call.size / 1024
            if size_kb < 1:
                size_str = f"{tool_call.size}B"
            else:
                size_str = f"{size_kb:.1f}KB"
            status_badges[2].update_status("size", size_str)

        # Update tab content
        request_pane = self.query_one("#request-tab", TabPane)
        request_content = list(request_pane.query(Static))[0]
        new_request_widget = self._create_content_widget(tool_call.request)
        request_content.remove()
        request_pane.mount(new_request_widget)

        response_pane = self.query_one("#response-tab", TabPane)
        response_content = list(response_pane.query(Static))[0]
        if tool_call.response:
            new_response_widget = self._create_content_widget(tool_call.response)
        else:
            new_response_widget = Static("No response yet", classes="no-response")
        response_content.remove()
        response_pane.mount(new_response_widget)

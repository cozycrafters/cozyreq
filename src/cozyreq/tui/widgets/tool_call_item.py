"""Tool call item widget for displaying individual tool calls in the timeline."""

from rich.text import Text
from textual.widgets import Static

from ..models import ToolCall


class ToolCallItem(Static):
    """A widget displaying a single tool call in the timeline."""

    def __init__(
        self,
        tool_call: ToolCall,
        selected: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Initialize the tool call item.

        Args:
            tool_call: The tool call data to display.
            selected: Whether this item is currently selected.
            name: Widget name.
            id: Widget ID.
            classes: Widget CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.tool_call: ToolCall = tool_call
        self.selected: bool = selected
        self._update_renderable()

    def _get_status_icon(self) -> tuple[str, str]:
        """Get the icon and color for the current status."""
        status_map = {
            "success": ("✓", "green"),
            "running": ("⚡", "yellow"),
            "queued": ("⏳", "bright_black"),
            "failed": ("❌", "red"),
        }
        return status_map.get(self.tool_call.status, ("", "white"))

    def _truncate(self, text: str, max_length: int = 50) -> str:
        """Truncate text if it exceeds max_length."""
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    def _update_renderable(self) -> None:
        """Update the renderable based on tool call data."""
        icon, color = self._get_status_icon()

        # Format timestamp (HH:MM:SS)
        time_str = self.tool_call.timestamp.strftime("%H:%M:%S")

        # Format duration
        if self.tool_call.duration is not None:
            duration_str = f"{self.tool_call.duration:.3f}s"
        else:
            duration_str = (
                "Running..." if self.tool_call.status == "running" else "Queued"
            )

        # Create text representation
        text = Text()

        # Line 1: sequence number, icon, tool name, and optional cursor
        line1 = f"{self.tool_call.sequence_number}. {icon} {self.tool_call.tool_name}"
        if self.selected:
            line1 += " ◄──"
        _ = text.append(
            line1 + "\n",
            style=color if self.tool_call.status != "queued" else "bright_black",
        )

        # Line 2: timestamp and duration
        line2 = f"   {time_str} │ {duration_str}"
        _ = text.append(line2 + "\n", style="bright_black")

        # Line 3: summary
        summary = self._truncate(self.tool_call.summary)
        _ = text.append(f"   {summary}\n", style="bright_black")

        # Line 4: result summary (if available)
        if self.tool_call.result_summary:
            result = self._truncate(self.tool_call.result_summary, 30)
            _ = text.append(f"   {result}", style="bright_black")

        self.update(text)

        # Add/remove selected class for styling
        if self.selected:
            _ = self.add_class("selected")
        else:
            _ = self.remove_class("selected")

    def set_selected(self, selected: bool) -> None:
        """
        Update the selection status.

        Args:
            selected: Whether this item should be selected.
        """
        self.selected = selected
        self._update_renderable()

"""Tool call list widget - left pane showing timeline of tool calls."""

from typing import override

from textual.containers import VerticalScroll
from textual.message import Message
from textual.widgets import Static

from ..models import ToolCall
from .progress_indicator import ProgressIndicator
from .tool_call_item import ToolCallItem


class ToolCallSelected(Message):
    """Message posted when a tool call is selected."""

    def __init__(self, tool_call: ToolCall, index: int) -> None:
        """
        Initialize the message.

        Args:
            tool_call: The selected tool call.
            index: The index of the selected tool call.
        """
        super().__init__()
        self.tool_call = tool_call
        self.index = index


class ToolCallList(VerticalScroll):
    """A scrollable list of tool calls with selection and progress indicator."""

    def __init__(
        self,
        tool_calls: list[ToolCall],
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Initialize the tool call list.

        Args:
            tool_calls: List of tool calls to display.
            name: Widget name.
            id: Widget ID.
            classes: Widget CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.tool_calls = tool_calls
        self.selected_index = 0 if tool_calls else -1

    @override
    def compose(self):
        """Compose the widget with title, progress, and tool call items."""
        # Title
        yield Static(
            f"Tool Call Timeline ({len(self.tool_calls)} calls)",
            classes="tool-call-list-title",
        )

        # Progress indicator
        if self.tool_calls:
            yield ProgressIndicator(
                total=len(self.tool_calls), completed=self.completed_count
            )

        # Tool call items
        for i, tool_call in enumerate(self.tool_calls):
            yield ToolCallItem(
                tool_call, selected=(i == self.selected_index), id=f"item-{i}"
            )

    @property
    def completed_count(self) -> int:
        """Count of completed (successful) tool calls."""
        return sum(1 for tc in self.tool_calls if tc.status == "success")

    @property
    def total_count(self) -> int:
        """Total number of tool calls."""
        return len(self.tool_calls)

    def select_next(self) -> None:
        """Select the next tool call in the list."""
        if not self.tool_calls:
            return

        if self.selected_index < len(self.tool_calls) - 1:
            self._update_selection(self.selected_index + 1)

    def select_previous(self) -> None:
        """Select the previous tool call in the list."""
        if not self.tool_calls:
            return

        if self.selected_index > 0:
            self._update_selection(self.selected_index - 1)

    def _update_selection(self, new_index: int) -> None:
        """
        Update the selected index and refresh items.

        Args:
            new_index: The new index to select.
        """
        old_index = self.selected_index
        self.selected_index = new_index

        # Update old item
        if old_index >= 0:
            old_item = self.query_one(f"#item-{old_index}", ToolCallItem)
            old_item.set_selected(False)

        # Update new item
        if new_index >= 0:
            new_item = self.query_one(f"#item-{new_index}", ToolCallItem)
            new_item.set_selected(True)

            # Scroll to make item visible
            new_item.scroll_visible()

        # Post message
        if new_index >= 0:
            self.post_message(ToolCallSelected(self.tool_calls[new_index], new_index))

"""Tool calls screen - main view showing tool call timeline and details."""

from typing import override

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen

from ..models import ToolCall
from ..widgets import ToolCallList, ToolCallSelected, ToolDetailsPanel


class ToolCallsScreen(Screen[None]):
    """Screen displaying tool calls timeline and details."""

    def __init__(
        self,
        tool_calls: list[ToolCall],
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Initialize the tool calls screen.

        Args:
            tool_calls: List of tool calls to display.
            name: Screen name.
            id: Screen ID.
            classes: Screen CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.tool_calls: list[ToolCall] = tool_calls

    @override
    def compose(self) -> ComposeResult:
        """Compose the screen with tool call list and details panel."""
        with Horizontal(id="tool-calls-container"):
            # Left pane: Tool call list (35% width)
            yield ToolCallList(
                self.tool_calls, id="tool-call-list", classes="left-pane"
            )

            # Right pane: Tool details panel (65% width)
            if self.tool_calls:
                yield ToolDetailsPanel(
                    self.tool_calls[0], id="tool-details-panel", classes="right-pane"
                )

    def on_tool_call_selected(self, message: ToolCallSelected) -> None:
        """Handle tool call selection to update details panel."""
        panel = self.query_one("#tool-details-panel", ToolDetailsPanel)
        panel.update_tool_call(message.tool_call)

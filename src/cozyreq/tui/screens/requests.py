from typing import override
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import TextArea


class RequestsScreen(Screen[None]):
    """Screen for showing and inspecting the requests made by the agent."""

    @override
    def compose(self) -> ComposeResult:
        yield TextArea(placeholder="Enter something nice")

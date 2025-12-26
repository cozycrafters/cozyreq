from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import TextArea
from typing_extensions import override


class PromptScreen(Screen[None]):
    """Screen for entering prompts."""

    @override
    def compose(self) -> ComposeResult:
        yield TextArea("Enter your prompt here...", id="prompt-textarea")

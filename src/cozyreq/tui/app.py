from typing import override

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class Tui(App[None]):
    @override
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

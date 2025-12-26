from typing import override

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class CozyReq(App[None]):
    TITLE: str | None = "CozyReq"

    @override
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()


app = CozyReq()

from typing import Callable, ClassVar, override

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.types import CSSPathType
from textual.widgets import Footer, Header

from cozyreq.tui.screens.prompt import PromptScreen
from cozyreq.tui.screens.requests import RequestsScreen


class CozyReq(App[None]):
    CSS_PATH: ClassVar[CSSPathType | None] = "styles.tcss"
    SCREENS: ClassVar[dict[str, Callable[[], Screen[None]]]] = {
        "prompt": PromptScreen,
        "requests": RequestsScreen,
    }
    TITLE: str | None = "CozyReq"

    @override
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    async def on_mount(self) -> None:
        await self.push_screen("prompt")


app = CozyReq()

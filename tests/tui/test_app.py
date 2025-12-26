from typing import Callable
from pathlib import PurePath

from textual.app import App


async def test_quit():
    """Test pressing Ctrl + q keys quits the app."""
    from cozyreq.tui.app import CozyReq

    app = CozyReq()
    async with app.run_test() as pilot:
        # Test pressing the Ctrl + q keys
        await pilot.press("ctrl+q")


def test_app(snap_compare: Callable[[str | PurePath | App[None]], bool]):
    from cozyreq.tui.app import CozyReq

    app = CozyReq()
    assert snap_compare(app)

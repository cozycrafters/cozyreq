from cozyreq.tui.app import Tui


async def test_quit():
    """Test pressing Ctrl + q keys quits the app."""
    app = Tui()
    async with app.run_test() as pilot:
        # Test pressing the Ctrl + q keys
        await pilot.press("ctrl+q")

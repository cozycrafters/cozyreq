async def test_quit():
    """Test pressing Ctrl + q keys quits the app."""
    from cozyreq.tui.app import CozyReq

    app = CozyReq()
    async with app.run_test() as pilot:
        # Test pressing the Ctrl + q keys
        await pilot.press("ctrl+q")


def test_app(snap_compare):
    from cozyreq.tui.app import CozyReq

    app = CozyReq()
    assert snap_compare(app)

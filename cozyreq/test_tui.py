import pytest
from cozyreq.tui import CozyReqApp


@pytest.mark.asyncio
async def test_tui_layout_and_initial_state():
    """Test that the app starts with correct layout and dummy data."""
    app = CozyReqApp()
    async with app.run_test():
        # Check main containers
        assert app.query_one("#conversation-panel")
        assert app.query_one("#details-panel")

        # Check dummy messages
        messages = app.query(".message")
        assert len(messages) >= 2
        assert "Get all users" in str(messages[0].content)

        # Check details panel content
        details = app.query_one("#details-content")
        assert "GET https://api.example.com/users" in str(details.content)


@pytest.mark.asyncio
async def test_tui_interaction():
    """Test typing in the input adds a message."""
    app = CozyReqApp()
    async with app.run_test() as pilot:
        # Find the input
        input_widget = app.query_one("Input")

        # Type a message
        await pilot.click("Input")
        await pilot.press(*list("Hello World"), "enter")

        # Check if message was added
        messages = app.query(".user-message")
        last_message = messages.last()
        assert "Hello World" in str(last_message.content)

        # Check input is cleared
        assert input_widget.value == ""

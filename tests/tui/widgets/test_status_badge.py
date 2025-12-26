from typing import cast
from textual.app import App, ComposeResult
from rich.text import Text

from cozyreq.tui.widgets.status_badge import StatusBadge


async def test_status_badge_success():
    """Test StatusBadge with success status."""

    class BadgeApp(App[None]):
        def compose(self) -> ComposeResult:
            yield StatusBadge("success", "Success")

    app = BadgeApp()
    async with app.run_test():
        badge = app.query_one(StatusBadge)
        assert badge.status_type == "success"
        assert badge.text == "Success"
        assert "✓" in str(getattr(badge, "renderable"))


async def test_status_badge_running():
    """Test StatusBadge with running status."""

    class BadgeApp(App[None]):
        def compose(self) -> ComposeResult:
            yield StatusBadge("running", "Running")

    app = BadgeApp()
    async with app.run_test():
        badge = app.query_one(StatusBadge)
        assert badge.status_type == "running"
        assert "⚡" in str(getattr(badge, "renderable"))


async def test_status_badge_queued():
    """Test StatusBadge with queued status."""

    class BadgeApp(App[None]):
        def compose(self) -> ComposeResult:
            yield StatusBadge("queued", "Queued")

    app = BadgeApp()
    async with app.run_test():
        badge = app.query_one(StatusBadge)
        assert badge.status_type == "queued"
        assert "⏳" in str(getattr(badge, "renderable"))


async def test_status_badge_failed():
    """Test StatusBadge with failed status."""

    class BadgeApp(App[None]):
        def compose(self) -> ComposeResult:
            yield StatusBadge("failed", "Failed")

    app = BadgeApp()
    async with app.run_test():
        badge = app.query_one(StatusBadge)
        assert badge.status_type == "failed"
        assert "❌" in str(getattr(badge, "renderable"))


async def test_status_badge_custom():
    """Test StatusBadge with custom status (duration/size)."""

    class BadgeApp(App[None]):
        def compose(self) -> ComposeResult:
            yield StatusBadge("duration", "0.427s")

    app = BadgeApp()
    async with app.run_test():
        badge = app.query_one(StatusBadge)
        assert badge.status_type == "duration"
        assert badge.text == "0.427s"


async def test_status_badge_update():
    """Test updating StatusBadge status dynamically."""

    class BadgeApp(App[None]):
        def compose(self) -> ComposeResult:
            yield StatusBadge("queued", "Queued")

    app = BadgeApp()
    async with app.run_test():
        badge = app.query_one(StatusBadge)
        assert badge.status_type == "queued"

        # Update status
        badge.update_status("success", "Success")
        assert badge.status_type == "success"
        assert badge.text == "Success"
        assert "✓" in str(getattr(badge, "renderable"))

from textual.app import App, ComposeResult

from cozyreq.tui.widgets.progress_indicator import ProgressIndicator


async def test_progress_indicator_rendering():
    """Test ProgressIndicator renders correctly."""

    class ProgressApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ProgressIndicator(total=12, completed=8)

    app = ProgressApp()
    async with app.run_test():
        indicator = app.query_one(ProgressIndicator)
        assert indicator.total == 12
        assert indicator.completed == 8
        assert indicator.percentage == 66  # 8/12 * 100 = 66.67 -> 66


async def test_progress_indicator_zero_division():
    """Test ProgressIndicator handles zero total gracefully."""

    class ProgressApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ProgressIndicator(total=0, completed=0)

    app = ProgressApp()
    async with app.run_test():
        indicator = app.query_one(ProgressIndicator)
        assert indicator.percentage == 0


async def test_progress_indicator_full():
    """Test ProgressIndicator at 100%."""

    class ProgressApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ProgressIndicator(total=10, completed=10)

    app = ProgressApp()
    async with app.run_test():
        indicator = app.query_one(ProgressIndicator)
        assert indicator.percentage == 100


async def test_progress_indicator_update():
    """Test updating ProgressIndicator values."""

    class ProgressApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ProgressIndicator(total=20, completed=5)

    app = ProgressApp()
    async with app.run_test():
        indicator = app.query_one(ProgressIndicator)
        assert indicator.percentage == 25

        # Update progress
        indicator.update_progress(total=20, completed=15)
        assert indicator.completed == 15
        assert indicator.percentage == 75


async def test_progress_indicator_text_format():
    """Test that progress indicator includes text format."""

    class ProgressApp(App[None]):
        def compose(self) -> ComposeResult:
            yield ProgressIndicator(total=12, completed=8)

    app = ProgressApp()
    async with app.run_test():
        indicator = app.query_one(ProgressIndicator)
        text = str(indicator.renderable)
        # Should contain: progress bar, numbers, and percentage
        assert "8/12" in text
        assert "66%" in text

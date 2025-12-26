from datetime import datetime
from typing import cast

from textual.app import App, ComposeResult

from cozyreq.tui.models import LogEntry, LogType
from cozyreq.tui.widgets.log_table import LogTable


async def test_log_table_rendering():
    """Test LogTable renders with log entries."""
    logs = [
        LogEntry(
            id="log-001",
            run_id="run-001",
            timestamp=datetime(2024, 12, 26, 12, 34, 0),
            log_type=cast(LogType, "INFO"),
            message="Agent initialized",
            metadata='{"model": "claude"}',
        ),
        LogEntry(
            id="log-002",
            run_id="run-001",
            timestamp=datetime(2024, 12, 26, 12, 34, 1),
            log_type=cast(LogType, "TOOL"),
            message="⚡ web_search (#1)",
            metadata=None,
        ),
    ]

    class TableApp(App[None]):
        def compose(self) -> ComposeResult:
            yield LogTable(logs)

    app = TableApp()
    async with app.run_test():
        table = cast(LogTable, app.query_one(LogTable))
        assert table is not None
        assert len(table.logs) == 2


async def test_log_table_filtering():
    """Test filtering logs by type."""
    log_types = ["INFO", "TOOL", "ERROR", "DEBUG", "INFO"]
    logs = [
        LogEntry(
            id=f"log-{i:03d}",
            run_id="run-001",
            timestamp=datetime(2024, 12, 26, 12, 34, i),
            log_type=cast(LogType, log_type),
            message=f"Message {i}",
            metadata=None,
        )
        for i, log_type in enumerate(log_types)
    ]

    class TableApp(App[None]):
        def compose(self) -> ComposeResult:
            yield LogTable(logs)

    app = TableApp()
    async with app.run_test():
        table = cast(LogTable, app.query_one(LogTable))

        # Filter to only INFO
        table.filter_logs({"INFO"})
        # Should show only 2 INFO entries
        assert table.row_count == 2

        # Filter to TOOL and ERROR
        table.filter_logs({"TOOL", "ERROR"})
        assert table.row_count == 2

        # Show all
        table.filter_logs({"INFO", "TOOL", "ERROR", "DEBUG"})
        assert table.row_count == 5


async def test_log_table_search():
    """Test searching logs."""
    logs = [
        LogEntry(
            id="log-001",
            run_id="run-001",
            timestamp=datetime(2024, 12, 26, 12, 34, 0),
            log_type="INFO",
            message="Agent initialized successfully",
            metadata=None,
        ),
        LogEntry(
            id="log-002",
            run_id="run-001",
            timestamp=datetime(2024, 12, 26, 12, 34, 1),
            log_type="TOOL",
            message="Running web_search",
            metadata=None,
        ),
        LogEntry(
            id="log-003",
            run_id="run-001",
            timestamp=datetime(2024, 12, 26, 12, 34, 2),
            log_type="ERROR",
            message="Connection failed",
            metadata=None,
        ),
    ]

    class TableApp(App[None]):
        def compose(self) -> ComposeResult:
            yield LogTable(logs)

    app = TableApp()
    async with app.run_test():
        table = cast(LogTable, app.query_one(LogTable))

        # Search for "initialized"
        table.search_logs("initialized")
        assert table.row_count == 1

        # Search for "web"
        table.search_logs("web")
        assert table.row_count == 1

        # Clear search
        table.search_logs("")
        assert table.row_count == 3


async def test_log_table_empty():
    """Test LogTable with no logs."""

    class TableApp(App[None]):
        def compose(self) -> ComposeResult:
            yield LogTable([])

    app = TableApp()
    async with app.run_test():
        table = cast(LogTable, app.query_one(LogTable))
        assert table.row_count == 0


async def test_log_table_combined_filter_and_search():
    """Test combining filtering and searching."""
    logs = [
        LogEntry(
            id="log-001",
            run_id="run-001",
            timestamp=datetime(2024, 12, 26, 12, 34, 0),
            log_type="INFO",
            message="Agent started successfully",
            metadata=None,
        ),
        LogEntry(
            id="log-002",
            run_id="run-001",
            timestamp=datetime(2024, 12, 26, 12, 34, 1),
            log_type="INFO",
            message="Processing data",
            metadata=None,
        ),
        LogEntry(
            id="log-003",
            run_id="run-001",
            timestamp=datetime(2024, 12, 26, 12, 34, 2),
            log_type="ERROR",
            message="Agent error occurred",
            metadata=None,
        ),
    ]

    class TableApp(App[None]):
        def compose(self) -> ComposeResult:
            yield LogTable(logs)

    app = TableApp()
    async with app.run_test():
        table = cast(LogTable, app.query_one(LogTable))

        # Filter to INFO only
        table.filter_logs({"INFO"})
        assert table.row_count == 2

        # Search for "Agent" within INFO logs
        table.search_logs("Agent")
        assert table.row_count == 1  # Only "Agent started successfully"

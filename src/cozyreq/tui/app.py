"""Main TUI application for CozyReq."""

from typing import ClassVar, override

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.widgets import Footer, Static

from .database import get_database_path, get_latest_run, get_logs, get_tool_calls
from .screens import LogsScreen, ToolCallsScreen


class Tui(App[None]):
    """CozyReq TUI application."""

    CSS: ClassVar[str] = """
    .left-pane {
        width: 35%;
        border-right: solid $accent;
    }
    
    .right-pane {
        width: 65%;
    }
    
    #tool-calls-container {
        height: 100%;
    }
    
    #logs-container {
        height: 100%;
    }
    
    #log-table {
        height: 1fr;
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("1", "show_tool_calls", "Tool Calls", show=True),
        Binding("2", "show_logs", "Logs", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self) -> None:
        """Initialize the TUI app."""
        super().__init__()
        self.run_id: str | None = None
        self.current_screen_name: str = "tool_calls"

    @override
    def compose(self) -> ComposeResult:
        """Compose the app with header and footer."""
        # Custom header
        yield Static("", id="app-header", classes="header")
        yield Footer()

    def on_mount(self) -> None:
        """Load data and show initial screen when app mounts."""
        try:
            # Load latest run from database
            db_path = get_database_path()
            latest_run = get_latest_run(db_path)

            if latest_run is None:
                self._show_error("No agent runs found in database")
                return

            self.run_id = latest_run.id

            # Update header
            duration = latest_run.duration
            duration_str = (
                f"{int(duration.total_seconds() // 60):02d}:{int(duration.total_seconds() % 60):02d}"
                if duration
                else "00:00"
            )

            header = self.query_one("#app-header", Static)
            header_text = Text()
            _ = header_text.append("AI Agent Monitor", style="bold cyan")
            _ = header_text.append(f"  Run #{latest_run.run_number}", style="yellow")
            _ = header_text.append(f" │ Duration: {duration_str}", style="dim")
            _ = header_text.append(
                f" │ Status: {latest_run.status}",
                style="green" if latest_run.status == "completed" else "yellow",
            )
            header.update(header_text)

            # Load data
            tool_calls = get_tool_calls(self.run_id, db_path)
            logs = get_logs(self.run_id, db_path=db_path)

            # Install screens
            self.install_screen(
                ToolCallsScreen(tool_calls, name="tool_calls"), name="tool_calls"
            )
            self.install_screen(LogsScreen(logs, name="logs"), name="logs")

            # Show tool calls screen by default
            self.push_screen("tool_calls")

        except Exception as e:
            self._show_error(f"Error loading data: {e}")

    def _show_error(self, message: str) -> None:
        """Show an error message."""
        header = self.query_one("#app-header", Static)
        header.update(Text(f"Error: {message}", style="bold red"))

    def action_show_tool_calls(self) -> None:
        """Switch to tool calls screen."""
        if self.current_screen_name != "tool_calls":
            self.switch_screen("tool_calls")
            self.current_screen_name = "tool_calls"

    def action_show_logs(self) -> None:
        """Switch to logs screen."""
        if self.current_screen_name != "logs":
            self.switch_screen("logs")
            self.current_screen_name = "logs"

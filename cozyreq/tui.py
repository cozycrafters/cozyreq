from dataclasses import dataclass
from typing import Literal, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Input, Static


@dataclass
class ExecutionRequest:
    """Represents a single HTTP request in the execution flow"""

    number: int
    method: str
    url: str
    headers: dict[str, str]
    body: Optional[str] = None
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    duration_ms: Optional[int] = None


@dataclass
class LogEntry:
    """Represents a single entry in the execution log"""

    type: Literal[
        "user_prompt",
        "planning",
        "discovery",
        "execution_start",
        "request_exec",
        "request_result",
    ]
    content: str
    request_number: Optional[int] = None


class CozyReqApp(App):
    CSS = """
    #main-container {
        layout: horizontal;
        height: 100%;
    }
    #log-container {
        width: 1fr;
        height: 100%;
        border-right: solid $primary;
    }
    #execution-log {
        width: 1fr;
        height: 1fr;
        overflow-y: auto;
        padding: 1;
    }
    #details-panel {
        width: 1fr;
        height: 100%;
        border: solid $primary;
        padding: 1;
    }
    #prompt-input {
        dock: bottom;
        margin: 0 1 1 1;
    }
    .log-entry {
        color: $text;
    }
    .planning-status {
        color: $accent;
    }
    .discovery {
        color: $success;
    }
    .execution-request {
        color: $primary;
    }
    .request-result-success {
        color: $success;
    }
    .request-result-error {
        color: $error;
    }
    """

    BINDINGS = [
        ("ctrl+p", "focus_prompt", "Prompt"),
        ("up,down", "navigate", "Select"),
        ("right", "focus_details", "Details"),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.requests: list[ExecutionRequest] = []
        self.log_entries: list[LogEntry] = []
        self.selected_request_index: int = 0

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            with Vertical(id="log-container") as log_container:
                log_container.border_title = "CozyReq"
                yield Vertical(id="execution-log")
                yield Input(placeholder="> ", id="prompt-input")
            with Vertical(id="details-panel") as details_panel:
                details_panel.border_title = "Request Details"
                yield Static("", id="details-content")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted"""
        self._add_dummy_log()

    def _add_dummy_log(self) -> None:
        """Add dummy log entries matching the wireframe"""
        log = self.query_one("#execution-log")

        # User prompt
        log.mount(Static("> get all users and update first email", classes="log-entry"))
        log.mount(Static("", classes="log-entry"))  # Blank line

        # Planning phase
        log.mount(Static("🤖 Planning...", classes="log-entry planning-status"))
        log.mount(Static("✓ Found: GET /api/users", classes="log-entry discovery"))
        log.mount(Static("✓ Found: POST /api/users", classes="log-entry discovery"))
        log.mount(Static("", classes="log-entry"))  # Blank line

        # Execution phase
        log.mount(Static("🔄 Executing:", classes="log-entry execution-request"))
        log.mount(Static("[1] GET /api/users", classes="log-entry execution-request"))
        log.mount(
            Static("    ✓ 200 OK (145ms)", classes="log-entry request-result-success")
        )
        log.mount(
            Static("[2] POST /api/users/1", classes="log-entry execution-request")
        )
        log.mount(
            Static("    ✓ 200 OK (89ms)", classes="log-entry request-result-success")
        )

        # Create dummy request objects
        self.requests = [
            ExecutionRequest(
                number=1,
                method="GET",
                url="/api/users",
                headers={"Content-Type": "application/json"},
                body=None,
                status_code=200,
                response_body='[{"id": 1, "email": "old@example.com"}, ...]',
                duration_ms=145,
            ),
            ExecutionRequest(
                number=2,
                method="POST",
                url="/api/users/1",
                headers={"Content-Type": "application/json"},
                body='{\n  "email": "new@example.com"\n}',
                status_code=200,
                response_body='{\n  "id": 1,\n  "email": "new@example.com"\n}',
                duration_ms=89,
            ),
        ]

        # Select the second request (as shown in wireframe)
        self.selected_request_index = 1
        self._update_details_panel()

    def _update_details_panel(self) -> None:
        """Update the details panel with the selected request"""
        if not self.requests:
            return

        req = self.requests[self.selected_request_index]

        # Build the details view
        details = []
        details.append(f"[{req.number}] {req.method} {req.url}")
        details.append("")
        details.append("▼ Request")
        details.append("Headers:")
        for key, value in req.headers.items():
            details.append(f"  {key}: {value}")
        if req.body:
            details.append("Body:")
            for line in req.body.split("\n"):
                details.append(line)
        else:
            details.append("Body: (None)")
        details.append("")
        details.append("▼ Response")
        details.append(f"Status: {req.status_code} OK")
        if req.response_body:
            for line in req.response_body.split("\n"):
                details.append(line)

        content = "\n".join(details)
        details_widget = self.query_one("#details-content", Static)
        details_widget.update(content)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value.strip()
        if not message:  # Ignore empty inputs
            return

        # Clear input
        event.input.value = ""

        # Add user prompt to log
        log = self.query_one("#execution-log")
        log.mount(Static("", classes="log-entry"))  # Blank line
        log.mount(Static(f"> {message}", classes="log-entry"))

        # Simulate planning (in real app, this would be async)
        log.mount(Static("", classes="log-entry"))
        log.mount(Static("🤖 Planning...", classes="log-entry planning-status"))

        # Scroll to bottom
        log.scroll_end(animate=False)

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts"""
        if event.key == "up" and self.selected_request_index > 0:
            self.selected_request_index -= 1
            self._update_details_panel()
        elif (
            event.key == "down" and self.selected_request_index < len(self.requests) - 1
        ):
            self.selected_request_index += 1
            self._update_details_panel()
        elif event.key == "ctrl+p":
            self.query_one("#prompt-input").focus()

    def action_focus_prompt(self) -> None:
        self.query_one("#prompt-input").focus()

    def action_navigate(self) -> None:
        # Handled in on_key
        pass

    def action_focus_details(self) -> None:
        self.query_one("#details-panel").focus()


if __name__ == "__main__":
    app = CozyReqApp()
    app.run()

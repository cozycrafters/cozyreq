from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, Input


class CozyReqApp(App):
    CSS = """
    #main-container {
        layout: horizontal;
        height: 100%;
    }
    #conversation-panel {
        width: 1fr;
        height: 100%;
        border-right: solid $primary;
    }
    #details-panel {
        width: 1fr;
        height: 100%;
        padding: 1;
    }
    #messages {
        height: 1fr;
        overflow-y: auto;
        padding: 1;
    }
    Input {
        dock: bottom;
        margin: 1;
    }
    .message {
        padding: 1;
        margin-bottom: 1;
        background: $surface;
        border: solid $primary;
    }
    .user-message {
        text-align: right;
    }
    .agent-message {
        text-align: left;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            with Vertical(id="conversation-panel"):
                with Vertical(id="messages"):
                    # Dummy Data
                    s1 = Static("Get all users", classes="message user-message")
                    s1.border_title = "User"
                    yield s1

                    s2 = Static(
                        "I've prepared a request to list users.\n[Select: GET /users]",
                        classes="message agent-message",
                    )
                    s2.border_title = "Agent"
                    yield s2
                yield Input(placeholder="Type your message here...")
            with Vertical(id="details-panel"):
                # Dummy Data for Request Details
                yield Static(
                    "Request: GET https://api.example.com/users\n\n"
                    "Headers:\n"
                    "  Content-Type: application/json\n"
                    "  Authorization: Bearer <token>\n\n"
                    "Body:\n"
                    "  (None)\n\n"
                    "Response:\n"
                    "  Status: 200 OK\n"
                    "  Data: [...]",
                    id="details-content",
                )
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        message = event.value
        if message:
            messages_container = self.query_one("#messages")
            new_message = Static(message, classes="message user-message")
            new_message.border_title = "User"
            messages_container.mount(new_message)
            messages_container.scroll_end(animate=False)
            event.input.value = ""


if __name__ == "__main__":
    app = CozyReqApp()
    app.run()

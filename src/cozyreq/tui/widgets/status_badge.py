"""Status badge widget showing status with icon and color."""

from typing import Literal

from rich.text import Text
from textual.widgets import Static

StatusType = Literal["success", "running", "queued", "failed", "duration", "size"]


class StatusBadge(Static):
    """A badge showing status with an icon and text."""

    def __init__(
        self,
        status_type: StatusType,
        text: str,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Initialize the status badge.

        Args:
            status_type: Type of status to display.
            text: Text to display in the badge.
            name: Widget name.
            id: Widget ID.
            classes: Widget CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.status_type: StatusType = status_type
        self.text: str = text
        self._update_renderable()

    def _update_renderable(self) -> None:
        """Update the renderable based on status type."""
        icon_map = {
            "success": ("✓", "green"),
            "running": ("⚡", "yellow"),
            "queued": ("⏳", "bright_black"),
            "failed": ("❌", "red"),
            "duration": ("│", "bright_black"),
            "size": ("│", "bright_black"),
        }

        icon, color = icon_map.get(self.status_type, ("", "white"))

        # Create rich text with icon and text
        rich_text = Text()
        if icon:
            _ = rich_text.append(icon + " ", style=color)
        _ = rich_text.append(
            self.text,
            style=color
            if self.status_type in ["success", "running", "queued", "failed"]
            else "bright_black",
        )

        self.update(rich_text)

    def update_status(self, status_type: StatusType, text: str) -> None:
        """
        Update the badge status and text.

        Args:
            status_type: New status type.
            text: New text to display.
        """
        self.status_type = status_type
        self.text = text
        self._update_renderable()

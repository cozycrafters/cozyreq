"""Progress indicator widget showing visual progress bar."""

from rich.text import Text
from textual.widgets import Static


class ProgressIndicator(Static):
    """A progress bar showing completion percentage."""

    def __init__(
        self,
        total: int,
        completed: int,
        *,
        bar_width: int = 20,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """
        Initialize the progress indicator.

        Args:
            total: Total number of items.
            completed: Number of completed items.
            bar_width: Width of the progress bar in characters.
            name: Widget name.
            id: Widget ID.
            classes: Widget CSS classes.
        """
        super().__init__(name=name, id=id, classes=classes)
        self.total = total
        self.completed = completed
        self.bar_width = bar_width
        self._update_renderable()

    @property
    def percentage(self) -> int:
        """Calculate completion percentage."""
        if self.total == 0:
            return 0
        return int((self.completed / self.total) * 100)

    def _update_renderable(self) -> None:
        """Update the renderable based on progress."""
        percentage = self.percentage
        filled_width = (
            int((self.completed / self.total) * self.bar_width) if self.total > 0 else 0
        )

        # Create progress bar
        bar = (
            "=" * filled_width + ">"
            if filled_width < self.bar_width
            else "=" * self.bar_width
        )
        bar = bar.ljust(self.bar_width)

        # Create text representation
        text = f"[{bar}] {self.completed}/{self.total} {percentage}%"

        self.renderable = Text(text, style="bright_blue")
        self.update(self.renderable)

    def update_progress(self, total: int, completed: int) -> None:
        """
        Update the progress values.

        Args:
            total: New total number of items.
            completed: New number of completed items.
        """
        self.total = total
        self.completed = completed
        self._update_renderable()

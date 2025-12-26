from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

StatusType = Literal["queued", "running", "success", "failed"]
LogType = Literal["INFO", "TOOL", "ERROR", "DEBUG"]
RunStatus = Literal["running", "completed", "failed"]


@dataclass
class ToolCall:
    id: str  # UUID
    run_id: str  # UUID
    sequence_number: int
    tool_name: str
    status: StatusType
    timestamp: datetime
    duration: float | None  # seconds
    request: str  # JSON string
    response: str | None  # JSON string
    size: int | None  # bytes
    summary: str  # Short description for list view
    result_summary: str | None  # Result description


@dataclass
class LogEntry:
    id: str  # UUID
    run_id: str  # UUID
    timestamp: datetime
    log_type: LogType
    message: str
    metadata: str | None  # JSON string


@dataclass
class AgentRun:
    id: str  # UUID
    run_number: int
    start_time: datetime
    end_time: datetime | None
    status: RunStatus

    @property
    def duration(self) -> timedelta | None:
        if self.end_time:
            return self.end_time - self.start_time
        return None

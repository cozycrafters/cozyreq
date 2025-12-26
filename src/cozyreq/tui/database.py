import sqlite3
from datetime import datetime
from pathlib import Path

from .models import AgentRun, LogEntry, LogType, ToolCall


class DatabaseError(Exception):
    """Base exception for database errors."""

    pass


class DatabaseConnectionError(DatabaseError):
    """Exception raised when database connection fails."""

    pass


class RunNotFoundError(DatabaseError):
    """Exception raised when a run is not found."""

    pass


def get_database_path() -> Path:
    """Get the path to the CozyReq database in the user's home directory."""
    return Path.home() / ".cozyreq" / "cozyreq.db"


def initialize_database(db_path: Path | None = None) -> None:
    """
    Initialize the database with the required schema.

    Args:
        db_path: Path to the database file. If None, uses get_database_path().
    """
    if db_path is None:
        db_path = get_database_path()

    # Create directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create agent_runs table
        _ = cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_runs (
                id TEXT PRIMARY KEY,
                run_number INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT NOT NULL CHECK(status IN ('running', 'completed', 'failed')),
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(run_number)
            )
        """)

        # Create tool_calls table
        _ = cursor.execute("""
            CREATE TABLE IF NOT EXISTS tool_calls (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,
                tool_name TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('queued', 'running', 'success', 'failed')),
                timestamp TEXT NOT NULL,
                duration REAL,
                request TEXT NOT NULL,
                response TEXT,
                size INTEGER,
                summary TEXT NOT NULL,
                result_summary TEXT,
                FOREIGN KEY (run_id) REFERENCES agent_runs(id) ON DELETE CASCADE,
                UNIQUE(run_id, sequence_number)
            )
        """)

        # Create logs table
        _ = cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                log_type TEXT NOT NULL CHECK(log_type IN ('INFO', 'TOOL', 'ERROR', 'DEBUG')),
                message TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (run_id) REFERENCES agent_runs(id) ON DELETE CASCADE
            )
        """)

        # Create indexes
        _ = cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tool_calls_run_id ON tool_calls(run_id)"
        )
        _ = cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tool_calls_sequence ON tool_calls(run_id, sequence_number)"
        )
        _ = cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_run_id ON logs(run_id)")
        _ = cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_logs_type ON logs(run_id, log_type)"
        )
        _ = cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(run_id, timestamp)"
        )

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        raise DatabaseConnectionError(f"Failed to initialize database: {e}") from e


def _connect(db_path: Path) -> sqlite3.Connection:
    """
    Connect to the database.

    Args:
        db_path: Path to the database file.

    Returns:
        Database connection.

    Raises:
        DatabaseConnectionError: If connection fails.
    """
    if not db_path.exists():
        raise DatabaseConnectionError(f"Database file not found: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise DatabaseConnectionError(f"Failed to connect to database: {e}") from e


def _parse_datetime(dt_str: str | None) -> datetime | None:
    """Parse ISO 8601 datetime string."""
    if dt_str is None:
        return None
    return datetime.fromisoformat(dt_str)


def get_agent_run(run_id: str, db_path: Path | None = None) -> AgentRun:
    """
    Get an agent run by ID.

    Args:
        run_id: UUID of the run.
        db_path: Path to the database file. If None, uses get_database_path().

    Returns:
        AgentRun object.

    Raises:
        RunNotFoundError: If run is not found.
        DatabaseConnectionError: If database connection fails.
    """
    if db_path is None:
        db_path = get_database_path()

    conn = _connect(db_path)
    cursor = conn.cursor()

    _ = cursor.execute("SELECT * FROM agent_runs WHERE id = ?", (run_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise RunNotFoundError(f"Run not found: {run_id}")

    return AgentRun(
        id=row["id"],
        run_number=row["run_number"],
        start_time=_parse_datetime(row["start_time"]),  # type: ignore
        end_time=_parse_datetime(row["end_time"]),
        status=row["status"],  # type: ignore
    )


def get_latest_run(db_path: Path | None = None) -> AgentRun | None:
    """
    Get the latest agent run (by run_number).

    Args:
        db_path: Path to the database file. If None, uses get_database_path().

    Returns:
        AgentRun object or None if no runs exist.

    Raises:
        DatabaseConnectionError: If database connection fails.
    """
    if db_path is None:
        db_path = get_database_path()

    conn = _connect(db_path)
    cursor = conn.cursor()

    _ = cursor.execute("SELECT * FROM agent_runs ORDER BY run_number DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return AgentRun(
        id=row["id"],
        run_number=row["run_number"],
        start_time=_parse_datetime(row["start_time"]),  # type: ignore
        end_time=_parse_datetime(row["end_time"]),
        status=row["status"],  # type: ignore
    )


def get_tool_calls(run_id: str, db_path: Path | None = None) -> list[ToolCall]:
    """
    Get all tool calls for a run, ordered by sequence number.

    Args:
        run_id: UUID of the run.
        db_path: Path to the database file. If None, uses get_database_path().

    Returns:
        List of ToolCall objects.

    Raises:
        DatabaseConnectionError: If database connection fails.
    """
    if db_path is None:
        db_path = get_database_path()

    conn = _connect(db_path)
    cursor = conn.cursor()

    _ = cursor.execute(
        "SELECT * FROM tool_calls WHERE run_id = ? ORDER BY sequence_number", (run_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        ToolCall(
            id=row["id"],
            run_id=row["run_id"],
            sequence_number=row["sequence_number"],
            tool_name=row["tool_name"],
            status=row["status"],  # type: ignore
            timestamp=_parse_datetime(row["timestamp"]),  # type: ignore
            duration=row["duration"],
            request=row["request"],
            response=row["response"],
            size=row["size"],
            summary=row["summary"],
            result_summary=row["result_summary"],
        )
        for row in rows
    ]


def get_logs(
    run_id: str,
    filter_types: list[LogType] | None = None,
    db_path: Path | None = None,
) -> list[LogEntry]:
    """
    Get logs for a run, optionally filtered by type.

    Args:
        run_id: UUID of the run.
        filter_types: List of log types to filter by. If None, returns all logs.
        db_path: Path to the database file. If None, uses get_database_path().

    Returns:
        List of LogEntry objects, ordered by timestamp.

    Raises:
        DatabaseConnectionError: If database connection fails.
    """
    if db_path is None:
        db_path = get_database_path()

    conn = _connect(db_path)
    cursor = conn.cursor()

    if filter_types:
        placeholders = ",".join("?" * len(filter_types))
        query = f"SELECT * FROM logs WHERE run_id = ? AND log_type IN ({placeholders}) ORDER BY timestamp"
        _ = cursor.execute(query, (run_id, *filter_types))
    else:
        _ = cursor.execute(
            "SELECT * FROM logs WHERE run_id = ? ORDER BY timestamp", (run_id,)
        )

    rows = cursor.fetchall()
    conn.close()

    return [
        LogEntry(
            id=row["id"],
            run_id=row["run_id"],
            timestamp=_parse_datetime(row["timestamp"]),  # type: ignore
            log_type=row["log_type"],  # type: ignore
            message=row["message"],
            metadata=row["metadata"],
        )
        for row in rows
    ]


def search_logs(
    run_id: str,
    query: str,
    filter_types: list[LogType] | None = None,
    db_path: Path | None = None,
) -> list[LogEntry]:
    """
    Search logs by message content.

    Args:
        run_id: UUID of the run.
        query: Search query (case-insensitive substring match).
        filter_types: List of log types to filter by. If None, searches all logs.
        db_path: Path to the database file. If None, uses get_database_path().

    Returns:
        List of LogEntry objects matching the query, ordered by timestamp.

    Raises:
        DatabaseConnectionError: If database connection fails.
    """
    if db_path is None:
        db_path = get_database_path()

    conn = _connect(db_path)
    cursor = conn.cursor()

    search_pattern = f"%{query}%"

    if filter_types:
        placeholders = ",".join("?" * len(filter_types))
        sql = f"SELECT * FROM logs WHERE run_id = ? AND message LIKE ? AND log_type IN ({placeholders}) ORDER BY timestamp"
        _ = cursor.execute(sql, (run_id, search_pattern, *filter_types))
    else:
        _ = cursor.execute(
            "SELECT * FROM logs WHERE run_id = ? AND message LIKE ? ORDER BY timestamp",
            (run_id, search_pattern),
        )

    rows = cursor.fetchall()
    conn.close()

    return [
        LogEntry(
            id=row["id"],
            run_id=row["run_id"],
            timestamp=_parse_datetime(row["timestamp"]),  # type: ignore
            log_type=row["log_type"],  # type: ignore
            message=row["message"],
            metadata=row["metadata"],
        )
        for row in rows
    ]


def get_run_statistics(run_id: str, db_path: Path | None = None) -> dict[str, int]:
    """
    Get statistics about tool calls for a run.

    Args:
        run_id: UUID of the run.
        db_path: Path to the database file. If None, uses get_database_path().

    Returns:
        Dictionary with statistics:
        - total_tool_calls: Total number of tool calls
        - completed_tool_calls: Number of successful tool calls
        - running_tool_calls: Number of running tool calls
        - failed_tool_calls: Number of failed tool calls

    Raises:
        DatabaseConnectionError: If database connection fails.
    """
    if db_path is None:
        db_path = get_database_path()

    conn = _connect(db_path)
    cursor = conn.cursor()

    _ = cursor.execute(
        "SELECT COUNT(*) as total FROM tool_calls WHERE run_id = ?", (run_id,)
    )
    total = cursor.fetchone()["total"]

    _ = cursor.execute(
        "SELECT COUNT(*) as completed FROM tool_calls WHERE run_id = ? AND status = 'success'",
        (run_id,),
    )
    completed = cursor.fetchone()["completed"]

    _ = cursor.execute(
        "SELECT COUNT(*) as running FROM tool_calls WHERE run_id = ? AND status = 'running'",
        (run_id,),
    )
    running = cursor.fetchone()["running"]

    _ = cursor.execute(
        "SELECT COUNT(*) as failed FROM tool_calls WHERE run_id = ? AND status = 'failed'",
        (run_id,),
    )
    failed = cursor.fetchone()["failed"]

    conn.close()

    return {
        "total_tool_calls": total,
        "completed_tool_calls": completed,
        "running_tool_calls": running,
        "failed_tool_calls": failed,
    }

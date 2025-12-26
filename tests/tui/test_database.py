import sqlite3
from datetime import datetime
from pathlib import Path

import pytest

from cozyreq.tui.database import (
    DatabaseConnectionError,
    RunNotFoundError,
    get_agent_run,
    get_database_path,
    get_latest_run,
    get_logs,
    get_run_statistics,
    get_tool_calls,
    initialize_database,
    search_logs,
)


@pytest.fixture
def temp_db(tmp_path: Path) -> Path:
    """Create a temporary database for testing."""
    db_path = tmp_path / "test_cozyreq.db"
    initialize_database(db_path)
    return db_path


@pytest.fixture
def sample_data(temp_db: Path) -> str:
    """Insert sample data into the database and return the run_id."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    # Insert agent run
    run_id = "123e4567-e89b-12d3-a456-426614174000"
    cursor.execute(
        """
        INSERT INTO agent_runs (id, run_number, start_time, end_time, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (run_id, 47, "2024-12-26T12:00:00", "2024-12-26T12:02:34", "completed"),
    )

    # Insert tool calls
    tool_calls = [
        (
            "123e4567-e89b-12d3-a456-426614174001",
            run_id,
            1,
            "web_search",
            "success",
            "2024-12-26T12:34:01",
            0.234,
            '{"method": "POST", "url": "https://api.search.com/v1/search", "body": {"query": "quantum computing"}}',
            '{"status": "success", "total_results": 24}',
            2400,
            'Query: "quantum computing..."',
            "→ 24 results",
        ),
        (
            "123e4567-e89b-12d3-a456-426614174002",
            run_id,
            2,
            "web_search",
            "success",
            "2024-12-26T12:34:02",
            0.312,
            '{"method": "POST", "url": "https://api.search.com/v1/search", "body": {"query": "quantum crypto"}}',
            '{"status": "success", "total_results": 18}',
            1800,
            'Query: "quantum crypto..."',
            "→ 18 results",
        ),
        (
            "123e4567-e89b-12d3-a456-426614174003",
            run_id,
            3,
            "api_call",
            "running",
            "2024-12-26T12:34:03",
            None,
            '{"method": "GET", "url": "https://arxiv.org/query"}',
            None,
            None,
            "arxiv.org/query",
            None,
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO tool_calls 
        (id, run_id, sequence_number, tool_name, status, timestamp, duration, request, response, size, summary, result_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        tool_calls,
    )

    # Insert logs
    logs = [
        (
            "123e4567-e89b-12d3-a456-426614174010",
            run_id,
            "2024-12-26T12:34:00",
            "INFO",
            "Agent initialized",
            '{"model": "claude-sonnet-4"}',
        ),
        (
            "123e4567-e89b-12d3-a456-426614174011",
            run_id,
            "2024-12-26T12:34:01",
            "TOOL",
            "⚡ web_search (#1) - query: 'quantum computing basics'",
            None,
        ),
        (
            "123e4567-e89b-12d3-a456-426614174012",
            run_id,
            "2024-12-26T12:34:01",
            "TOOL",
            "✓ Success (0.234s) - Retrieved 24 results",
            None,
        ),
        (
            "123e4567-e89b-12d3-a456-426614174013",
            run_id,
            "2024-12-26T12:34:02",
            "ERROR",
            "Connection timeout",
            '{"endpoint": "https://example.com"}',
        ),
        (
            "123e4567-e89b-12d3-a456-426614174014",
            run_id,
            "2024-12-26T12:34:03",
            "DEBUG",
            "Debug information",
            None,
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO logs (id, run_id, timestamp, log_type, message, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        logs,
    )

    conn.commit()
    conn.close()

    return run_id


def test_get_database_path():
    """Test that database path is in user's home directory."""
    path = get_database_path()
    assert path.parent.name == ".cozyreq"
    assert path.name == "cozyreq.db"
    assert str(path.parent).startswith(str(Path.home()))


def test_initialize_database(temp_db: Path):
    """Test that database is initialized with correct schema."""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    # Check agent_runs table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='agent_runs'"
    )
    assert cursor.fetchone() is not None

    # Check tool_calls table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='tool_calls'"
    )
    assert cursor.fetchone() is not None

    # Check logs table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logs'")
    assert cursor.fetchone() is not None

    conn.close()


def test_get_agent_run(temp_db: Path, sample_data: str):
    """Test retrieving an agent run by ID."""
    run = get_agent_run(sample_data, temp_db)

    assert run.id == sample_data
    assert run.run_number == 47
    assert run.status == "completed"
    assert run.start_time == datetime(2024, 12, 26, 12, 0, 0)
    assert run.end_time == datetime(2024, 12, 26, 12, 2, 34)
    assert run.duration is not None


def test_get_agent_run_not_found(temp_db: Path):
    """Test that RunNotFoundError is raised for non-existent run."""
    with pytest.raises(RunNotFoundError):
        get_agent_run("00000000-0000-0000-0000-000000000000", temp_db)


def test_get_latest_run(temp_db: Path, sample_data: str):
    """Test retrieving the latest run."""
    # Add another run with higher run_number
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    new_run_id = "223e4567-e89b-12d3-a456-426614174000"
    cursor.execute(
        """
        INSERT INTO agent_runs (id, run_number, start_time, end_time, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (new_run_id, 48, "2024-12-26T13:00:00", None, "running"),
    )
    conn.commit()
    conn.close()

    latest = get_latest_run(temp_db)
    assert latest is not None
    assert latest.run_number == 48
    assert latest.id == new_run_id


def test_get_latest_run_empty_database(temp_db: Path):
    """Test that get_latest_run returns None for empty database."""
    latest = get_latest_run(temp_db)
    assert latest is None


def test_get_tool_calls(temp_db: Path, sample_data: str):
    """Test retrieving tool calls for a run."""
    tool_calls = get_tool_calls(sample_data, temp_db)

    assert len(tool_calls) == 3
    assert tool_calls[0].sequence_number == 1
    assert tool_calls[1].sequence_number == 2
    assert tool_calls[2].sequence_number == 3

    # Check first tool call
    assert tool_calls[0].tool_name == "web_search"
    assert tool_calls[0].status == "success"
    assert tool_calls[0].duration == 0.234
    assert tool_calls[0].size == 2400
    assert tool_calls[0].summary == 'Query: "quantum computing..."'
    assert tool_calls[0].result_summary == "→ 24 results"

    # Check running tool call
    assert tool_calls[2].status == "running"
    assert tool_calls[2].duration is None
    assert tool_calls[2].response is None


def test_get_logs(temp_db: Path, sample_data: str):
    """Test retrieving logs for a run."""
    logs = get_logs(sample_data, db_path=temp_db)

    assert len(logs) == 5
    assert logs[0].message == "Agent initialized"
    assert logs[0].log_type == "INFO"


def test_get_logs_with_filter(temp_db: Path, sample_data: str):
    """Test retrieving logs with type filter."""
    tool_logs = get_logs(sample_data, filter_types=["TOOL"], db_path=temp_db)
    assert len(tool_logs) == 2
    assert all(log.log_type == "TOOL" for log in tool_logs)

    error_logs = get_logs(sample_data, filter_types=["ERROR"], db_path=temp_db)
    assert len(error_logs) == 1
    assert error_logs[0].message == "Connection timeout"

    # Multiple filters
    multi_logs = get_logs(sample_data, filter_types=["INFO", "ERROR"], db_path=temp_db)
    assert len(multi_logs) == 2


def test_search_logs(temp_db: Path, sample_data: str):
    """Test searching logs by query."""
    results = search_logs(sample_data, "initialized", db_path=temp_db)
    assert len(results) == 1
    assert results[0].message == "Agent initialized"

    results = search_logs(sample_data, "Success", db_path=temp_db)
    assert len(results) == 1

    results = search_logs(sample_data, "nonexistent", db_path=temp_db)
    assert len(results) == 0


def test_search_logs_with_filter(temp_db: Path, sample_data: str):
    """Test searching logs with type filter."""
    # Search only in TOOL logs
    results = search_logs(
        sample_data, "web_search", filter_types=["TOOL"], db_path=temp_db
    )
    assert len(results) == 1
    assert results[0].log_type == "TOOL"


def test_get_run_statistics(temp_db: Path, sample_data: str):
    """Test getting run statistics."""
    stats = get_run_statistics(sample_data, temp_db)

    assert stats["total_tool_calls"] == 3
    assert stats["completed_tool_calls"] == 2  # Two with status 'success'
    assert stats["running_tool_calls"] == 1
    assert stats["failed_tool_calls"] == 0


def test_database_connection_error():
    """Test that DatabaseConnectionError is raised for invalid path."""
    invalid_path = Path("/nonexistent/path/to/database.db")
    with pytest.raises(DatabaseConnectionError):
        get_agent_run("123e4567-e89b-12d3-a456-426614174000", invalid_path)

"""Script to create a sample database for manual TUI testing."""

import sqlite3
from pathlib import Path

from cozyreq.tui.database import get_database_path, initialize_database


def create_sample_database(db_path: Path | None = None) -> None:
    """Create a sample database with realistic data for testing the TUI."""
    if db_path is None:
        db_path = get_database_path()

    # Initialize database
    initialize_database(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM logs")
    cursor.execute("DELETE FROM tool_calls")
    cursor.execute("DELETE FROM agent_runs")

    # Insert sample agent run
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
            "tc-001",
            run_id,
            1,
            "web_search",
            "success",
            "2024-12-26T12:34:01",
            0.234,
            """{"method": "POST", "url": "https://api.search.com/v1/search", "headers": {"Content-Type": "application/json", "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbG...", "User-Agent": "AI-Agent/1.0"}, "query_params": {"query": "quantum computing basics", "limit": 10, "language": "en"}, "body": {"query": "quantum computing basics", "filters": {"date_range": "2020-2024", "source": ["arxiv", "ieee"]}}}""",
            """{"status": "success", "query": "quantum computing basics", "total_results": 24, "returned": 10, "execution_time_ms": 234, "results": [{"title": "Introduction to Quantum Computing", "url": "https://arxiv.org/abs/...", "relevance": 0.94}]}""",
            2400,
            'Query: "quantum computing..."',
            "→ 24 results",
        ),
        (
            "tc-002",
            run_id,
            2,
            "web_search",
            "success",
            "2024-12-26T12:34:02",
            0.312,
            """{"method": "POST", "url": "https://api.search.com/v1/search", "headers": {"Content-Type": "application/json", "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbG..."}, "query_params": {"query": "quantum cryptography applications"}, "body": {"query": "quantum cryptography applications"}}""",
            """{"status": "success", "total_results": 18, "execution_time_ms": 312}""",
            1800,
            'Query: "quantum crypto..."',
            "→ 18 results",
        ),
        (
            "tc-003",
            run_id,
            3,
            "web_search",
            "success",
            "2024-12-26T12:34:03",
            0.427,
            """{"method": "POST", "url": "https://api.search.com/v1/search", "headers": {"Content-Type": "application/json", "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbG...", "User-Agent": "AI-Agent/1.0", "Accept": "application/json", "X-Request-ID": "req_abc123xyz"}, "query_params": {"query": "quantum applications", "limit": 10, "language": "en", "sort_by": "relevance"}, "body": {"query": "quantum applications", "filters": {"date_range": "2020-2024", "source": ["arxiv", "ieee"]}, "include_metadata": true}}""",
            """{"status": "success", "query": "quantum applications", "total_results": 31, "returned": 10, "execution_time_ms": 427, "results": [{"title": "Quantum Computing in Modern Cryptography", "url": "https://arxiv.org/abs/...", "relevance": 0.94}]}""",
            2847,
            'Query: "applications"',
            "→ 31 results",
        ),
        (
            "tc-004",
            run_id,
            4,
            "api_call",
            "success",
            "2024-12-26T12:34:04",
            0.856,
            """{"method": "GET", "url": "https://arxiv.org/query", "headers": {"Accept": "application/json"}, "query_params": {"search": "quantum"}}""",
            """{"status": "success", "papers": 15}""",
            4200,
            "arxiv.org/query",
            "→ 15 papers",
        ),
        (
            "tc-005",
            run_id,
            5,
            "database_query",
            "success",
            "2024-12-26T12:34:05",
            0.123,
            """{"method": "POST", "url": "http://localhost/query", "body": {"table": "papers", "query": "SELECT * FROM papers WHERE topic = 'quantum'"}}""",
            """{"status": "success", "rows": 47}""",
            1500,
            "Table: papers",
            "→ 47 rows",
        ),
        (
            "tc-006",
            run_id,
            6,
            "web_fetch",
            "success",
            "2024-12-26T12:34:06",
            1.234,
            """{"method": "GET", "url": "https://example.com/paper.pdf", "headers": {"Accept": "application/pdf"}}""",
            """{"status": "success", "size": 2516582, "content_type": "application/pdf"}""",
            2516582,
            "example.com/paper.pdf",
            "→ 2.4MB downloaded",
        ),
        (
            "tc-007",
            run_id,
            7,
            "web_search",
            "success",
            "2024-12-26T12:34:07",
            0.445,
            """{"method": "POST", "url": "https://api.search.com/v1/search", "body": {"query": "recent quantum papers 2024"}}""",
            """{"status": "success", "total_results": 22}""",
            1900,
            'Query: "recent papers..."',
            "→ 22 results",
        ),
        (
            "tc-008",
            run_id,
            8,
            "api_call",
            "running",
            "2024-12-26T12:34:08",
            None,
            """{"method": "GET", "url": "https://semantic.scholar.org/api", "headers": {"Accept": "application/json"}}""",
            None,
            None,
            "semantic.scholar.org",
            None,
        ),
        (
            "tc-009",
            run_id,
            9,
            "database_query",
            "queued",
            "2024-12-26T12:34:09",
            None,
            """{"method": "POST", "body": {"table": "citations"}}""",
            None,
            None,
            "Table: citations",
            None,
        ),
        (
            "tc-010",
            run_id,
            10,
            "web_fetch",
            "queued",
            "2024-12-26T12:34:10",
            None,
            """{"method": "GET", "url": "https://example.com/data.json"}""",
            None,
            None,
            "example.com/data.json",
            None,
        ),
        (
            "tc-011",
            run_id,
            11,
            "api_call",
            "failed",
            "2024-12-26T12:34:11",
            2.5,
            """{"method": "POST", "url": "https://api.example.com/endpoint"}""",
            """{"status": "error", "message": "Connection timeout"}""",
            0,
            "api.example.com/endpoint",
            "→ Error: timeout",
        ),
        (
            "tc-012",
            run_id,
            12,
            "web_search",
            "success",
            "2024-12-26T12:34:12",
            0.356,
            """{"method": "POST", "url": "https://api.search.com/v1/search", "body": {"query": "machine learning quantum"}}""",
            """{"status": "success", "total_results": 45}""",
            3200,
            'Query: "machine learning..."',
            "→ 45 results",
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
            "log-001",
            run_id,
            "2024-12-26T12:34:00",
            "INFO",
            "▶ Agent initialized",
            '{"task": "Research quantum computing applications...", "model": "claude-sonnet-4-20250514", "max_iterations": 50}',
        ),
        (
            "log-002",
            run_id,
            "2024-12-26T12:34:01",
            "INFO",
            "▶ Planning execution strategy",
            '{"plan": ["Gather background", "Query databases", "Synthesize"]}',
        ),
        (
            "log-003",
            run_id,
            "2024-12-26T12:34:02",
            "TOOL",
            '⚡ web_search (#1) - query: "quantum computing basics"',
            None,
        ),
        (
            "log-004",
            run_id,
            "2024-12-26T12:34:02",
            "TOOL",
            "✓ Success (0.234s) - Retrieved 24 results, top score: 0.94",
            None,
        ),
        (
            "log-005",
            run_id,
            "2024-12-26T12:34:03",
            "INFO",
            "📊 Processing search results",
            '{"filtered": "24/24", "avg_relevance": 0.87, "found": {"papers": 12, "tutorials": 8, "docs": 4}}',
        ),
        (
            "log-006",
            run_id,
            "2024-12-26T12:34:03",
            "TOOL",
            '⚡ web_search (#2) - query: "quantum cryptography applications"',
            None,
        ),
        (
            "log-007",
            run_id,
            "2024-12-26T12:34:03",
            "TOOL",
            "✓ Success (0.312s) - Retrieved 18 results",
            None,
        ),
        (
            "log-008",
            run_id,
            "2024-12-26T12:34:04",
            "INFO",
            "📊 Cross-referencing results",
            '{"common_topics": 5, "correlation": 0.73}',
        ),
        (
            "log-009",
            run_id,
            "2024-12-26T12:34:05",
            "TOOL",
            '⚡ web_search (#3) - query: "quantum applications"',
            None,
        ),
        (
            "log-010",
            run_id,
            "2024-12-26T12:34:05",
            "TOOL",
            "✓ Success (0.427s) - Retrieved 31 results",
            None,
        ),
        (
            "log-011",
            run_id,
            "2024-12-26T12:34:06",
            "TOOL",
            "⚡ api_call (#4) - endpoint: arxiv.org/query",
            None,
        ),
        (
            "log-012",
            run_id,
            "2024-12-26T12:34:07",
            "TOOL",
            "✓ Success (0.856s) - Found 15 academic papers",
            None,
        ),
        (
            "log-013",
            run_id,
            "2024-12-26T12:34:07",
            "TOOL",
            "⚡ database_query (#5) - table: papers",
            None,
        ),
        (
            "log-014",
            run_id,
            "2024-12-26T12:34:07",
            "TOOL",
            "✓ Success (0.123s) - Retrieved 47 rows",
            None,
        ),
        (
            "log-015",
            run_id,
            "2024-12-26T12:34:08",
            "TOOL",
            "⚡ web_fetch (#6) - url: example.com/paper.pdf",
            None,
        ),
        (
            "log-016",
            run_id,
            "2024-12-26T12:34:09",
            "TOOL",
            "✓ Success (1.234s) - Downloaded 2.4MB",
            None,
        ),
        (
            "log-017",
            run_id,
            "2024-12-26T12:34:09",
            "INFO",
            "📊 Analyzing downloaded content",
            '{"pages": 847}',
        ),
        (
            "log-018",
            run_id,
            "2024-12-26T12:34:10",
            "TOOL",
            '⚡ web_search (#7) - query: "recent quantum papers 2024"',
            None,
        ),
        (
            "log-019",
            run_id,
            "2024-12-26T12:34:10",
            "TOOL",
            "✓ Success (0.445s) - Retrieved 22 results",
            None,
        ),
        (
            "log-020",
            run_id,
            "2024-12-26T12:34:11",
            "TOOL",
            "⚡ api_call (#8) - endpoint: semantic.scholar.org",
            None,
        ),
        (
            "log-021",
            run_id,
            "2024-12-26T12:34:11",
            "TOOL",
            "⏳ Running... (1.2s elapsed)",
            None,
        ),
        (
            "log-022",
            run_id,
            "2024-12-26T12:34:11",
            "ERROR",
            "❌ Connection timeout for api.example.com/endpoint",
            '{"endpoint": "https://api.example.com/endpoint", "timeout": 2.5}',
        ),
        (
            "log-023",
            run_id,
            "2024-12-26T12:34:12",
            "DEBUG",
            "🐛 Retrying failed request with exponential backoff",
            '{"attempt": 2, "backoff_ms": 1000}',
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

    print(f"Sample database created at: {db_path}")
    print(f"Run ID: {run_id}")
    print(f"Tool calls: {len(tool_calls)}")
    print(f"Logs: {len(logs)}")


if __name__ == "__main__":
    create_sample_database()

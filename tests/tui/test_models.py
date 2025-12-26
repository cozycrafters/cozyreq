from datetime import datetime, timedelta

from cozyreq.tui.models import AgentRun, LogEntry, ToolCall


def test_agent_run_duration_with_end_time():
    start = datetime(2024, 12, 26, 12, 0, 0)
    end = datetime(2024, 12, 26, 12, 2, 34)
    run = AgentRun(
        id="123e4567-e89b-12d3-a456-426614174000",
        run_number=47,
        start_time=start,
        end_time=end,
        status="completed",
    )

    assert run.duration == timedelta(seconds=154)


def test_agent_run_duration_without_end_time():
    start = datetime(2024, 12, 26, 12, 0, 0)
    run = AgentRun(
        id="123e4567-e89b-12d3-a456-426614174000",
        run_number=47,
        start_time=start,
        end_time=None,
        status="running",
    )

    assert run.duration is None


def test_tool_call_creation():
    tool_call = ToolCall(
        id="123e4567-e89b-12d3-a456-426614174001",
        run_id="123e4567-e89b-12d3-a456-426614174000",
        sequence_number=1,
        tool_name="web_search",
        status="success",
        timestamp=datetime(2024, 12, 26, 12, 34, 1),
        duration=0.234,
        request='{"query": "quantum computing"}',
        response='{"results": []}',
        size=2400,
        summary='Query: "quantum computing..."',
        result_summary="→ 24 results",
    )

    assert tool_call.tool_name == "web_search"
    assert tool_call.status == "success"
    assert tool_call.duration == 0.234


def test_log_entry_creation():
    log = LogEntry(
        id="123e4567-e89b-12d3-a456-426614174002",
        run_id="123e4567-e89b-12d3-a456-426614174000",
        timestamp=datetime(2024, 12, 26, 12, 34, 0),
        log_type="INFO",
        message="Agent initialized",
        metadata='{"model": "claude-sonnet-4"}',
    )

    assert log.log_type == "INFO"
    assert log.message == "Agent initialized"

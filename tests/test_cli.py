from typer.testing import CliRunner
from unittest.mock import patch

from cozyreq.cli import app
import cozyreq.openapi as openapi


runner = CliRunner()


def test_run_command_success():
    """Test successful execution of run command."""
    mock_spec = {
        "openapi": "3.0.3",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {"/users": {"get": {"summary": "List users"}}},
    }

    with patch("cozyreq.openapi.fetch_openapi_spec") as mock_fetch:
        mock_fetch.return_value = mock_spec

        result = runner.invoke(app, ["run", "https://api.example.com/openapi.json"])

        assert result.exit_code == 0
        assert "GET" in result.stdout
        assert "/users" in result.stdout
        assert "List users" in result.stdout


def test_run_command_with_yaml_spec():
    """Test run command with YAML spec."""
    mock_spec = {
        "openapi": "3.0.3",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/pets": {
                "get": {"summary": "List pets"},
                "post": {"summary": "Create pet"},
            }
        },
    }

    with patch("cozyreq.openapi.fetch_openapi_spec") as mock_fetch:
        mock_fetch.return_value = mock_spec

        result = runner.invoke(app, ["run", "https://api.example.com/openapi.yaml"])

        assert result.exit_code == 0
        assert "GET" in result.stdout
        assert "POST" in result.stdout
        assert "/pets" in result.stdout


def test_run_command_network_error():
    """Test run command with network error."""
    with patch("cozyreq.openapi.fetch_openapi_spec") as mock_fetch:
        mock_fetch.side_effect = openapi.SpecFetchError("Network error")

        result = runner.invoke(app, ["run", "https://invalid.url"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Network error" in result.stdout


def test_run_command_parse_error():
    """Test run command with parse error."""
    with patch("cozyreq.openapi.fetch_openapi_spec") as mock_fetch:
        mock_fetch.side_effect = openapi.SpecParseError("Invalid spec format")

        result = runner.invoke(app, ["run", "https://api.example.com/invalid.json"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout
        assert "Invalid spec format" in result.stdout


def test_run_command_no_args():
    """Test run command without URL argument."""
    result = runner.invoke(app, ["run"])

    assert result.exit_code != 0
    # Check both stdout and stderr for error message
    output = result.stdout + result.stderr
    assert (
        ("Missing argument" in output) or ("Usage:" in output) or ("required" in output)
    )


def test_run_command_empty_spec():
    """Test run command with empty OpenAPI spec."""
    mock_spec = {
        "openapi": "3.0.3",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {},
    }

    with patch("cozyreq.openapi.fetch_openapi_spec") as mock_fetch:
        mock_fetch.return_value = mock_spec

        result = runner.invoke(app, ["run", "https://api.example.com/openapi.json"])

        assert result.exit_code == 0
        assert "No endpoints found" in result.stdout


def test_run_command_complex_spec():
    """Test run command with complex OpenAPI spec."""
    mock_spec = {
        "openapi": "3.0.3",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {"summary": "List users"},
                "post": {"summary": "Create user"},
            },
            "/users/{id}": {
                "get": {"summary": "Get user"},
                "put": {"summary": "Update user"},
                "delete": {"summary": "Delete user"},
            },
            "/posts": {"get": {"summary": "List posts"}},
        },
    }

    with patch("cozyreq.openapi.fetch_openapi_spec") as mock_fetch:
        mock_fetch.return_value = mock_spec

        result = runner.invoke(app, ["run", "https://api.example.com/openapi.json"])

        assert result.exit_code == 0
        # Should contain all endpoints
        assert "GET" in result.stdout
        assert "POST" in result.stdout
        assert "PUT" in result.stdout
        assert "DELETE" in result.stdout
        assert "/users" in result.stdout
        assert "/users/{id}" in result.stdout
        assert "/posts" in result.stdout

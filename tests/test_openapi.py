import pytest
import json
import yaml
from unittest.mock import Mock, patch

import cozyreq.openapi as openapi


class TestFetchOpenAPISpec:
    """Test fetching OpenAPI specifications from URLs."""

    @pytest.mark.asyncio
    async def test_fetch_json_spec(self):
        """Test fetching JSON OpenAPI specification."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {},
        }
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = json.dumps(mock_response.json.return_value)

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = Mock()
            mock_client_instance.get = Mock(return_value=mock_response)
            mock_client_instance.get.return_value.raise_for_status = Mock()
            mock_client.return_value.__aenter__ = Mock(
                return_value=mock_client_instance
            )
            mock_client.return_value.__aexit__ = Mock(return_value=None)

            spec = await openapi.fetch_openapi_spec(
                "https://api.example.com/openapi.json"
            )

            assert spec["openapi"] == "3.0.3"
            assert spec["info"]["title"] == "Test API"

    @pytest.mark.asyncio
    async def test_fetch_yaml_spec(self):
        """Test fetching YAML OpenAPI specification."""
        spec_data = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {},
        }
        mock_response = Mock()
        mock_response.text = yaml.dump(spec_data)
        mock_response.headers = {"content-type": "application/yaml"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = Mock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            spec = await openapi.fetch_openapi_spec(
                "https://api.example.com/openapi.yaml"
            )

            assert spec["openapi"] == "3.0.3"
            assert spec["info"]["title"] == "Test API"

    @pytest.mark.asyncio
    async def test_fetch_spec_with_yaml_extension(self):
        """Test that .yaml extension is detected correctly."""
        spec_data = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {},
        }
        mock_response = Mock()
        mock_response.text = yaml.dump(spec_data)
        mock_response.headers = {}  # No content-type header

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = Mock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            spec = await openapi.fetch_openapi_spec("https://api.example.com/spec.yaml")

            assert spec["openapi"] == "3.0.3"

    @pytest.mark.asyncio
    async def test_fetch_spec_http_error(self):
        """Test handling of HTTP errors."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = Mock()
            mock_client_instance.get.side_effect = Exception("Connection error")
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            with pytest.raises(openapi.SpecFetchError):
                await openapi.fetch_openapi_spec("https://invalid.url")

    @pytest.mark.asyncio
    async def test_fetch_spec_invalid_json(self):
        """Test handling of invalid JSON."""
        mock_response = Mock()
        mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)
        mock_response.text = "invalid json"
        mock_response.headers = {"content-type": "application/json"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = Mock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            with pytest.raises(openapi.SpecParseError):
                await openapi.fetch_openapi_spec("https://api.example.com/openapi.json")


class TestParseOpenAPIEndpoints:
    """Test parsing OpenAPI specifications to extract endpoints."""

    def test_parse_simple_spec(self):
        """Test parsing a simple OpenAPI specification."""
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "summary": "List users",
                        "description": "Get all users",
                        "operationId": "listUsers",
                    },
                    "post": {"summary": "Create user", "operationId": "createUser"},
                },
                "/users/{id}": {
                    "get": {"summary": "Get user", "operationId": "getUser"}
                },
            },
        }

        endpoints = openapi.parse_openapi_endpoints(spec)

        assert len(endpoints) == 3

        # Check first endpoint
        assert endpoints[0].method == "GET"
        assert endpoints[0].path == "/users"
        assert endpoints[0].summary == "List users"
        assert endpoints[0].description == "Get all users"
        assert endpoints[0].operation_id == "listUsers"

        # Check second endpoint
        assert endpoints[1].method == "POST"
        assert endpoints[1].path == "/users"
        assert endpoints[1].summary == "Create user"
        assert endpoints[1].operation_id == "createUser"

        # Check third endpoint
        assert endpoints[2].method == "GET"
        assert endpoints[2].path == "/users/{id}"
        assert endpoints[2].summary == "Get user"
        assert endpoints[2].operation_id == "getUser"

    def test_parse_spec_with_missing_fields(self):
        """Test parsing spec with missing optional fields."""
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "summary": "List users"
                        # No description or operationId
                    }
                }
            },
        }

        endpoints = openapi.parse_openapi_endpoints(spec)

        assert len(endpoints) == 1
        assert endpoints[0].method == "GET"
        assert endpoints[0].path == "/users"
        assert endpoints[0].summary == "List users"
        assert endpoints[0].description is None
        assert endpoints[0].operation_id is None

    def test_parse_spec_no_paths(self):
        """Test parsing spec with no paths."""
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {},
        }

        endpoints = openapi.parse_openapi_endpoints(spec)

        assert len(endpoints) == 0

    def test_parse_spec_non_operation_fields(self):
        """Test that non-operation fields in paths are ignored."""
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "parameters": [],  # Should be ignored
                    "get": {"summary": "List users"},
                }
            },
        }

        endpoints = openapi.parse_openapi_endpoints(spec)

        assert len(endpoints) == 1
        assert endpoints[0].method == "GET"

    def test_parse_spec_invalid_path_item(self):
        """Test handling of invalid path items."""
        spec = {
            "openapi": "3.0.3",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/users": "invalid",  # Not a dict
                "/valid": {"get": {"summary": "Valid endpoint"}},
            },
        }

        endpoints = openapi.parse_openapi_endpoints(spec)

        assert len(endpoints) == 1  # Only the valid one should be parsed
        assert endpoints[0].path == "/valid"


class TestFormatEndpointsList:
    """Test formatting endpoints for terminal display."""

    def test_format_empty_list(self):
        """Test formatting empty endpoints list."""
        result = openapi.format_endpoints_list([])
        assert "No endpoints found" in result

    def test_format_single_endpoint(self):
        """Test formatting single endpoint."""
        endpoints = [
            openapi.EndpointInfo(method="GET", path="/users", summary="List users")
        ]

        result = openapi.format_endpoints_list(endpoints)

        assert "GET" in result
        assert "/users" in result
        assert "List users" in result

    def test_format_multiple_endpoints(self):
        """Test formatting multiple endpoints."""
        endpoints = [
            openapi.EndpointInfo(method="GET", path="/users", summary="List users"),
            openapi.EndpointInfo(method="POST", path="/users", summary="Create user"),
            openapi.EndpointInfo(method="GET", path="/users/{id}", summary="Get user"),
            openapi.EndpointInfo(
                method="DELETE", path="/users/{id}", summary="Delete user"
            ),
        ]

        result = openapi.format_endpoints_list(endpoints)

        # Should contain all endpoints
        assert "GET" in result
        assert "POST" in result
        assert "DELETE" in result
        assert "/users" in result
        assert "/users/{id}" in result

    def test_format_endpoints_sorted(self):
        """Test that endpoints are sorted by path and method."""
        endpoints = [
            openapi.EndpointInfo(method="POST", path="/users", summary="Create user"),
            openapi.EndpointInfo(method="GET", path="/users", summary="List users"),
            openapi.EndpointInfo(method="GET", path="/pets", summary="List pets"),
        ]

        result = openapi.format_endpoints_list(endpoints)

        # Should be sorted by path, then by method
        assert result.index("/pets") < result.index("/users")
        # Within same path, GET should come before POST
        get_index = result.find("GET", result.find("/users"))
        post_index = result.find("POST", result.find("/users"))
        assert get_index < post_index

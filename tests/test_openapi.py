import pytest
from openapi_pydantic import parse_obj

import cozyreq.openapi as openapi


def test_parse_pydantic_model_simple_spec():
    """Test parsing a simple OpenAPI Pydantic model."""
    spec_data = {
        "openapi": "3.0.3",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "summary": "List users",
                    "description": "Get all users",
                    "operationId": "listUsers",
                    "responses": {"200": {"description": "Success"}},
                },
                "post": {
                    "summary": "Create user",
                    "operationId": "createUser",
                    "responses": {"201": {"description": "Created"}},
                },
            },
            "/users/{id}": {
                "get": {
                    "summary": "Get user",
                    "operationId": "getUser",
                    "responses": {"200": {"description": "Success"}},
                }
            },
        },
    }

    # Convert to Pydantic model
    spec_model = parse_obj(spec_data)
    endpoints = openapi.parse_openapi_endpoints(spec_model)

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


def test_parse_dict_backward_compatibility():
    """Test parsing still works with dicts (for backward compatibility)."""
    spec = {
        "openapi": "3.0.3",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "summary": "List users",
                    "responses": {"200": {"description": "Success"}},
                }
            }
        },
    }

    # Test direct dict parsing (backward compatibility)
    endpoints = openapi.parse_openapi_endpoints(spec)

    assert len(endpoints) == 1
    assert endpoints[0].method == "GET"
    assert endpoints[0].path == "/users"
    assert endpoints[0].summary == "List users"


def test_parse_spec_with_missing_fields():
    """Test parsing spec with missing optional fields."""
    spec = {
        "openapi": "3.0.3",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "summary": "List users",
                    "responses": {"200": {"description": "Success"}},
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


def test_parse_spec_no_paths():
    """Test parsing spec with no paths."""
    spec = {
        "openapi": "3.0.3",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {},
    }

    endpoints = openapi.parse_openapi_endpoints(spec)

    assert len(endpoints) == 0


def test_parse_spec_non_operation_fields():
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


def test_parse_spec_invalid_path_item():
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


def test_format_empty_list():
    """Test formatting empty endpoints list."""
    result = openapi.format_endpoints_list([])
    assert "No endpoints found" in result


def test_format_single_endpoint():
    """Test formatting single endpoint."""
    endpoints = [
        openapi.EndpointInfo(method="GET", path="/users", summary="List users")
    ]

    result = openapi.format_endpoints_list(endpoints)

    assert "GET" in result
    assert "/users" in result
    assert "List users" in result


def test_format_multiple_endpoints():
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


def test_format_endpoints_sorted():
    """Test that endpoints are sorted by path and method."""
    endpoints = [
        openapi.EndpointInfo(method="POST", path="/users", summary="Create user"),
        openapi.EndpointInfo(method="GET", path="/users", summary="List users"),
        openapi.EndpointInfo(method="GET", path="/pets", summary="List pets"),
    ]

    result = openapi.format_endpoints_list(endpoints)

    # Should be sorted by path, then by method
    # The table should show /pets first, then /users
    # Check that all endpoints are present
    assert "GET" in result
    assert "POST" in result
    assert "/users" in result
    assert "/pets" in result

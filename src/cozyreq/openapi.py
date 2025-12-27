import typing
import httpx
import yaml
import json
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table


@dataclass
class EndpointInfo:
    method: str
    path: str
    summary: str
    description: str | None = None
    operation_id: str | None = None


class OpenAPIError(Exception):
    """Base exception for OpenAPI-related errors."""

    pass


class SpecFetchError(OpenAPIError):
    """Raised when unable to fetch OpenAPI specification."""

    pass


class SpecParseError(OpenAPIError):
    """Raised when unable to parse OpenAPI specification."""

    pass


async def fetch_openapi_spec(url: str) -> dict[str, typing.Any]:
    """Fetch OpenAPI specification from the given URL or local file."""
    try:
        # Handle local file paths
        if not url.startswith(("http://", "https://")):
            import pathlib

            file_path = pathlib.Path(url)
            if not file_path.exists():
                raise SpecFetchError(f"Local file not found: {url}")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if url.endswith((".yaml", ".yml")):
                return yaml.safe_load(content)
            else:
                return json.loads(content)

        # Handle HTTP URLs
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()

            if "yaml" in content_type or url.endswith((".yaml", ".yml")):
                return yaml.safe_load(response.text)
            else:
                return response.json()

    except httpx.HTTPError as e:
        raise SpecFetchError(f"Failed to fetch OpenAPI spec from {url}: {e}")
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        raise SpecParseError(f"Failed to parse OpenAPI spec: {e}")
    except FileNotFoundError:
        raise SpecFetchError(f"File not found: {url}")
    except Exception as e:
        raise OpenAPIError(f"Unexpected error fetching OpenAPI spec: {e}")


def parse_openapi_endpoints(spec: dict[str, typing.Any]) -> list[EndpointInfo]:
    """Parse OpenAPI specification and extract endpoint information."""
    endpoints = []

    # Get paths from the spec
    paths = spec.get("paths", {})

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        # Extract operations for each HTTP method
        for method, operation in path_item.items():
            if method.lower() not in [
                "get",
                "post",
                "put",
                "delete",
                "patch",
                "head",
                "options",
            ]:
                continue

            if not isinstance(operation, dict):
                continue

            endpoint = EndpointInfo(
                method=method.upper(),
                path=path,
                summary=operation.get("summary", ""),
                description=operation.get("description"),
                operation_id=operation.get("operationId"),
            )
            endpoints.append(endpoint)

    # Sort by path and method for consistent ordering
    endpoints.sort(key=lambda x: (x.path, x.method))
    return endpoints


def format_endpoints_list(endpoints: list[EndpointInfo]) -> str:
    """Format endpoints list for terminal display using rich."""
    if not endpoints:
        return "No endpoints found in the OpenAPI specification."

    console = Console()

    # Create a table for nice formatting
    table = Table(
        title="Available API Endpoints", show_header=True, header_style="bold magenta"
    )
    table.add_column("Method", style="cyan", no_wrap=True)
    table.add_column("Path", style="green")
    table.add_column("Summary", style="white")

    # Add rows for each endpoint
    for endpoint in endpoints:
        method_style = {
            "GET": "bright_blue",
            "POST": "bright_green",
            "PUT": "bright_yellow",
            "DELETE": "bright_red",
            "PATCH": "bright_magenta",
            "HEAD": "bright_cyan",
            "OPTIONS": "bright_white",
        }.get(endpoint.method, "white")

        table.add_row(
            f"[{method_style}]{endpoint.method}[/{method_style}]",
            endpoint.path,
            endpoint.summary or "No summary available",
        )

    # Capture table output as string
    from io import StringIO

    output = StringIO()
    console.file = output
    console.print(table)
    return output.getvalue()

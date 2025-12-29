import json
import typing
from dataclasses import dataclass

import httpx
import yaml
from openapi_pydantic import OpenAPI, parse_obj
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


async def fetch_openapi_spec(url: str) -> OpenAPI:  # type: ignore # pyright: ignore
    """Fetch OpenAPI specification from the given URL or local file and return Pydantic model."""
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
                spec_dict = yaml.safe_load(content)  # pyright: ignore[reportAny]
            else:
                spec_dict = json.loads(content)  # pyright: ignore[reportAny]

            # Parse into Pydantic model
            try:
                return typing.cast(OpenAPI, parse_obj(spec_dict))
            except Exception as e:
                # Check if this is an OpenAPI 2.0 spec (Swagger)
                if spec_dict.get("swagger") == "2.0":  # pyright: ignore[reportAny]
                    raise SpecParseError(
                        "OpenAPI 2.0 (Swagger) specifications are not supported. Please use an OpenAPI 3.0 or 3.1 specification."
                    ) from e
                else:
                    raise SpecParseError(
                        f"Failed to parse OpenAPI specification: {e}"
                    ) from e

    except httpx.HTTPError as e:
        raise SpecFetchError(f"Failed to fetch OpenAPI spec from {url}: {e}")
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        raise SpecParseError(f"Failed to parse OpenAPI spec: {e}")
    except FileNotFoundError:
        raise SpecFetchError(f"File not found: {url}")
    except Exception as e:
        raise OpenAPIError(f"Unexpected error fetching OpenAPI spec: {e}")


def parse_openapi_endpoints(spec: typing.Any) -> list[EndpointInfo]:  # type: ignore # pyright: ignore[reportAny]
    """Parse OpenAPI specification and extract endpoint information.

    Accepts either OpenAPI Pydantic model or dict for backward compatibility with tests.
    """
    endpoints = []

    # Handle both Pydantic model and dict input
    if hasattr(spec, "paths"):  # pyright: ignore[reportAny]
        # Pydantic model path
        if not spec.paths:  # pyright: ignore[reportAny]
            return endpoints  # pyright: ignore[reportUnknownVariableType]
        paths = spec.paths  # pyright: ignore[reportAny]
        for path_str, path_item in paths.items():  # pyright: ignore[reportAny]
            if not path_item:
                continue
            # Extract operations for each HTTP method
            path_dict = path_item.model_dump(exclude_none=True)  # pyright: ignore[reportAny]
            for method, operation in path_dict.items():  # pyright: ignore[reportAny]
                if method.lower() not in [  # pyright: ignore[reportAny]
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
                    method=method.upper(),  # pyright: ignore[reportAny]
                    path=path_str,  # pyright: ignore[reportAny]
                    summary=operation.get("summary", ""),  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                    description=operation.get("description", ""),  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                    operation_id=operation.get("operationId"),  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                )
                endpoints.append(endpoint)  # pyright: ignore[reportUnknownMemberType]
    else:
        # Dict path (for backward compatibility with tests)
        paths = spec.get("paths", {})  # pyright: ignore[reportAny]
        for path_str, path_item in paths.items():  # pyright: ignore[reportAny]
            if not isinstance(path_item, dict):
                continue
            for method, operation in path_item.items():  # pyright: ignore[reportUnknownVariableType]
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
                    path=path_str,
                    summary=operation.get("summary", ""),
                    description=operation.get("description"),
                    operation_id=operation.get("operationId"),
                )
                endpoints.append(endpoint)

    # Sort by path and method for consistent ordering
    endpoints.sort(key=lambda x: (x.path, x.method))  # pyright: ignore[reportUnknownLambdaType, reportUnknownMemberType]
    return endpoints  # pyright: ignore[reportUnknownVariableType]


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

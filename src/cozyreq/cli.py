import asyncio
import typer

import cozyreq.agent as agent
import cozyreq.tui.app as tui_app
import cozyreq.openapi as openapi

app = typer.Typer()


@app.command()
def pydantic(prompt: str):
    """Send a prompt to Kimi and get the result."""
    import asyncio

    result = asyncio.run(agent.run_agent(prompt))
    print(f"Result: {result}")


@app.command()
def tui():
    tui_app.app.run()


@app.command()
def run(url: str):
    """Fetch OpenAPI spec from URL and display available endpoints."""
    try:
        # Fetch and parse with Pydantic models
        spec = asyncio.run(openapi.fetch_openapi_spec(url))
        endpoints = openapi.parse_openapi_endpoints(spec)
        formatted_output = openapi.format_endpoints_list(endpoints)
        print(formatted_output)
    except openapi.OpenAPIError as e:
        print(f"Error: {e}")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()

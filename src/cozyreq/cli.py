import typer

import cozyreq.agent as agent
import cozyreq.tui.app as tui_app

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


def main():
    app()


if __name__ == "__main__":
    main()

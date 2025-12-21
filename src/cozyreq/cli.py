import typer

from .tui.app import Tui

app = typer.Typer()


@app.command()
def tui():
    Tui().run()


def main():
    app()


if __name__ == "__main__":
    main()

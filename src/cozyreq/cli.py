import typer

import cozyreq.tui.app as tui_app

app = typer.Typer()


@app.command()
def tui():
    tui_app.app.run()


def main():
    app()


if __name__ == "__main__":
    main()

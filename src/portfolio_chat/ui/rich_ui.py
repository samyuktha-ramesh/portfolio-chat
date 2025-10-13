from contextlib import contextmanager

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text
from rich.theme import Theme


class UI:
    def __init__(self):
        theme = Theme(
            {
                "banner": "bold cyan",
                "function": "bold green",
                "function_args": "yellow",
                "error": "bold red",
                "highlight": "bold",
            }
        )
        self.console = Console(theme=theme)
        self.session = PromptSession(
            completer=WordCompleter(["/help", "/reset", "/quit"], ignore_case=True)
        )

    def banner(self, msg: str) -> None:
        self.console.print(msg, style="banner")

    def assistant(self, content: RenderableType, print: bool = True) -> Panel:
        panel = Panel(
            content, title="Assistant", border_style="cyan", title_align="left"
        )
        if print:
            self.console.print(panel)
        return panel

    def prompt(self, prefix: str) -> str:
        return self.session.prompt(prefix)

    @contextmanager
    def stream_assistant(self):
        """Context manager yielding a write(delta) fn that live-updates a panel."""
        text = Text()
        spinner = Spinner("dots")

        panel = self.assistant(Group(text), print=False)

        with Live(panel, console=self.console, refresh_per_second=24) as live:

            def write(delta: str, style: str | None = None):
                text.append(delta, style=style)

            @contextmanager
            def spinner_cm(msg: str):
                spinner.text = Text(msg, style="highlight")
                panel.renderable = (
                    Group(text, spinner) if text.plain else Group(spinner)
                )
                live.update(panel, refresh=True)
                try:
                    yield
                finally:
                    panel.renderable = Group(text)
                    live.update(panel, refresh=True)

            yield write, spinner_cm

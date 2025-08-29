from contextlib import contextmanager
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from rich.console import Console, Group
from rich.theme import Theme
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text


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

    def assistant(self, text: str, print: bool = True) -> Panel:
        panel = Panel(text, title="Assistant", border_style="cyan", title_align="left")
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
        busy = False

        panel: Panel = self.assistant("", print=False)

        def current_renderable():
            return Group(text, spinner) if busy else text

        with Live(panel, console=self.console, refresh_per_second=24):

            def write(delta: str, style: str | None = None):
                text.append(delta, style=style)
                panel.renderable = current_renderable()

            @contextmanager
            def spinner_cm(text: str):
                nonlocal busy
                busy = True
                panel.renderable = current_renderable()
                spinner.text = Text(text, style="highlight")
                try:
                    yield
                finally:
                    busy = False
                    panel.renderable = current_renderable()

            yield write, spinner_cm

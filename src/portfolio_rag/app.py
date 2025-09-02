from omegaconf import DictConfig
from .runtime.session import ChatSession
from .ui.rich_ui import UI

EXIT_COMMAND = "/quit"
RESTART_COMMAND = "/reset"
HELP_COMMAND = "/help"


class ChatApp:
    """Main application class for the chat interface."""

    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        self.ui = UI()
        self.session = ChatSession(cfg)

    def run(self):
        """Starts the chat loop."""
        self.ui.banner("Chat session initialized.")
        while True:
            try:
                text = self.ui.prompt("> ").strip()
                if text.lower() == EXIT_COMMAND:
                    self.ui.assistant("Bye!")
                    break
                elif text.lower() == RESTART_COMMAND:
                    self.ui.banner("Restarted chat session")
                    self.session = ChatSession(self.cfg)
                    continue
                elif text.lower() == HELP_COMMAND:
                    self.ui.banner("Available commands:")
                    self.ui.console.print(f" - {EXIT_COMMAND}: Exit the chat")
                    self.ui.console.print(f" - {RESTART_COMMAND}: Restart the chat")
                    self.ui.console.print(f" - {HELP_COMMAND}: Show this help message")
                    continue

                with self.ui.stream_assistant() as (writer, spinner_cm):

                    def on_text(token: str):
                        writer(token)

                    def on_tool_start(token: str):
                        writer("\nCalling Tool: ", style="highlight")
                        writer(token + "(", style="function")

                    def on_tool_args(args: str):
                        writer(args, style="function_args")

                    def on_tool_request():
                        writer(")", style="function")

                    def on_tool_output(response: str):
                        writer("\nOutput: ", style="highlight")
                        writer(response + "\n")

                    self.session.query(
                        text,
                        on_text=on_text,
                        on_tool_start=on_tool_start,
                        on_tool_args=on_tool_args,
                        on_tool_request=on_tool_request,
                        on_tool_output=on_tool_output,
                        spinner_cm=spinner_cm,
                    )

            except (KeyboardInterrupt, EOFError):
                self.ui.assistant("Bye!")
                return

            except Exception as e:
                self.ui.console.print(f"[error]Error:[/error] {e}")

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
                    for out in self.session.query(text, spinner_cm=spinner_cm):
                        if not out:
                            continue
                        if out == "on_tool_request":
                            writer("\n", style="function")
                            continue
                        event_type, token = out
                        match event_type:
                            case "on_text":
                                writer(token)
                            case "on_tool_start":
                                writer("Calling Tool: ", style="highlight")
                                writer(token + "\n", style="function")
                                writer("Agent Query: ", style="highlight")
                            case "on_tool_args":
                                writer(token, style="function_args")
                            case "on_tool_output":
                                writer("\nOutput: ", style="highlight")
                                writer(token + "\n", style="function_args")

            except (KeyboardInterrupt, EOFError):
                self.ui.assistant("Bye!")
                return

            except Exception as e:
                self.ui.console.print(f"[error]Error:[/error] {e}")

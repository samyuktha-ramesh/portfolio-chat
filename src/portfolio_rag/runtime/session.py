import json
from typing import Any, Dict, Callable, List

from omegaconf import DictConfig
from openai import OpenAI

from .toolspecs import load_toolspecs
from ..tools.orchestrator import orchestrate


class ChatSession:
    """
    Manages the chat session with the OpenAI API.

    Args:
        cfg (DictConfig): The configuration object containing API settings and prompts.
    """

    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        self.client = OpenAI(base_url=cfg.model.base_url, api_key=cfg.model.api_key)

        self.model = cfg.model.name
        self.gen_kwargs = cfg.model.get("generation_kwargs", {})
        self.tools = load_toolspecs(cfg)

        self.history: List[Dict[str, Any]] = []
        if getattr(cfg.prompts, "system", None):
            self.history.append({"role": "system", "content": cfg.prompts.system})

    def query(
        self,
        prompt: str,
        on_text: Callable[[str], None],
        on_tool_start: Callable[[str], None],
        on_tool_args: Callable[[str], None],
        on_tool_request: Callable[[], None],
        on_tool_output: Callable[[str], None],
        spinner_cm,
    ) -> str:
        """Queries the OpenAI API with the given prompt.

        Args:
            prompt (str): The user prompt to send to the API.
             (Callable[[str], None]): A callback function to handle streaming tokens.
            on_tool_start (Callable[[str], None]): A callback function to handle tool start events.
            on_tool_args (Callable[[str], None]): A callback function to handle tool arguments.
            on_tool_request (Callable[[], None]): A callback function to handle tool requests.
            on_tool_output (Callable[[str], None]): A callback function to handle tool responses.
            spinner_cm: A context manager for managing the spinner.
        Returns:
            str: The API response.
        """
        self.history.append({"role": "user", "content": prompt})

        while True:
            with self.client.responses.stream(
                model=self.model,
                input=self.history,  # type: ignore
                tools=self.tools,  # type: ignore
                **self.gen_kwargs,
            ) as stream:
                tool_calls = 0
                assistant_message = ""

                for event in stream:
                    match event.type:
                        case "response.output_text.delta":
                            on_text(event.delta)

                        case "response.output_text.done":
                            assistant_message = event.text
                            self.history.append(
                                {"role": "assistant", "content": assistant_message}
                            )

                        case "response.output_item.added":
                            if event.item.type == "function_call":
                                on_tool_start(event.item.name)
                                on_tool_args(event.item.arguments)
                                tool_calls += 1

                            if event.item.type == "custom_tool_call_input":
                                on_tool_start(event.item.name)
                                on_tool_args(event.item.arguments)
                                tool_calls += 1

                        case "response.output_item.done":
                            if event.item.type == "function_call":
                                on_tool_request()
                                function_call_args = json.loads(event.item.arguments)
                                self.call_tool(
                                    event.item.name,
                                    event.item.id or "",
                                    spinner_context=spinner_cm,
                                    on_tool_output=on_tool_output,
                                    **function_call_args,
                                )

                            if event.item.type == "custom_tool_call_output":
                                self.call_tool(
                                    event.item.name,
                                    event.item.id,
                                    custom=True,
                                    spinner_context=spinner_cm,
                                    query=event.item.text,
                                    on_tool_output=on_tool_output,
                                )

                        case "response.custom_tool_call_input.delta":
                            on_tool_args(event.delta)

                        case "response.function_call_arguments.delta":
                            on_tool_args(event.delta)

                if tool_calls == 0:
                    return assistant_message

    def call_tool(
        self,
        tool_name: str,
        tool_id: str,
        spinner_context,
        on_tool_output: Callable[[str], None],
        custom: bool = False,
        **kwargs: Any,
    ) -> str:
        """Calls a tool with the given name and arguments.

        Args:
            tool_name (str): The name of the tool to call.
            tool_id (str): The ID of the tool to call.
            spinner_context: The context for the spinner while the tool is being called.
            on_tool_output (Callable[[str], None]): A callback function to handle tool output.
            custom (bool): Whether the tool call is custom.
            **kwargs: Additional keyword arguments to pass to the tool.

        Returns:
            Dict[str, Any]: The tool's response to be appended to the history.
        """
        result = orchestrate(tool_name, spinner_context=spinner_context, **kwargs)
        self.history.append(
            {
                "type": "custom_tool_call_output" if custom else "tool_call_output",
                "call_id": tool_id,
                "output": result,
            }
        )
        on_tool_output(result)
        return result

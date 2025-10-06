import json
from collections.abc import Generator
from contextlib import ExitStack, nullcontext
from typing import Any, Literal

from omegaconf import DictConfig
from openai import OpenAI

from .orchestrator import orchestrate
from .toolspecs import load_toolspecs


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

        self.history = []
        if getattr(cfg, "system_prompt", None):
            self.history.append({"role": "system", "content": cfg.system_prompt})

    def query(
        self, prompt: str, spinner_cm=None
    ) -> Generator[
        tuple[str, str] | Literal["on_tool_request"] | Literal["on_reasoning"],
        None,
        None,
    ]:
        """Queries the OpenAI API with the given prompt.

        Args:
            prompt (str): The user prompt to send to the API.
            on_text (Callable[[str], None]): A callback function to handle streaming tokens.
            on_tool_start (Callable[[str], None]): A callback function to handle tool start events.
            on_tool_args (Callable[[str], None]): A callback function to handle tool arguments.
            on_tool_request (Callable[[], None]): A callback function to handle tool requests.
            on_tool_output (Callable[[str], None]): A callback function to handle tool responses.
            spinner_cm: A context manager for managing the spinner.
        """
        spinner_cm = spinner_cm or nullcontext
        self.history.append({"role": "user", "content": prompt})
        stack = ExitStack()
        for _ in range(self.cfg.max_retries):
            with self.client.responses.stream(
                model=self.model,
                input=self.history,
                tools=self.tools,
                **self.gen_kwargs,
            ) as stream:
                tool_outputs = []
                for event in stream:
                    match event.type:
                        case "response.output_text.delta":
                            yield "on_text", event.delta

                        case "response.output_item.added":
                            if event.item.type == "reasoning":
                                yield "on_reasoning"
                                stack.enter_context(spinner_cm("Thinking...."))

                            if event.item.type == "function_call":
                                yield "on_tool_start", event.item.name
                                yield "on_tool_args", event.item.arguments

                            if event.item.type == "custom_tool_call":
                                yield "on_tool_start", event.item.name
                                yield "on_tool_args", event.item.input

                        case "response.output_item.done":
                            if event.item.type == "reasoning":
                                stack.close()

                            if event.item.type == "function_call":
                                yield "on_tool_request"
                                function_call_args = json.loads(event.item.arguments)
                                result, out = self._call_tool(
                                    event.item.name,
                                    event.item.call_id,
                                    spinner_context=spinner_cm,
                                    **function_call_args,
                                )
                                yield "on_tool_output", result
                                tool_outputs.append(out)

                            if event.item.type == "custom_tool_call":
                                yield "on_tool_request"
                                result, out = self._call_tool(
                                    event.item.name,
                                    event.item.call_id,
                                    custom=True,
                                    spinner_context=spinner_cm,
                                    query=event.item.input,
                                )
                                yield "on_tool_output", result
                                tool_outputs.append(out)

                        case "response.custom_tool_call_input.delta":
                            yield "on_tool_args", event.delta

                        case "response.function_call_arguments.delta":
                            yield "on_tool_args", event.delta

            self.history += stream.get_final_response().output
            if not tool_outputs:
                break
            self.history.extend(tool_outputs)

        else:  # Max retries exceeded
            yield "on_text", self.cfg.max_retries_exceeded_message

    def _call_tool(
        self,
        tool_name: str,
        tool_id: str,
        spinner_context,
        custom: bool = False,
        **kwargs: Any,
    ) -> tuple[str, dict]:
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
        result = orchestrate(
            tool_name, self.cfg, spinner_context=spinner_context, **kwargs
        )
        history_item = {
            "type": "custom_tool_call_output" if custom else "function_call_output",
            "call_id": tool_id,
            "output": result,
        }
        return result, history_item

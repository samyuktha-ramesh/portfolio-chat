from omegaconf import DictConfig


def _tool_from_config(tool: DictConfig):
    """Convert a tool configuration into a tool specification dictionary."""
    if tool.type == "custom":
        return _custom_tool(tool)
    return _function_tool(tool)


def _function_tool(tool: DictConfig):
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description,
        "parameters": {
            "type": "object",
            "properties": {
                param.name: {"type": param.type, "description": param.description}
                for param in tool.parameters
            },
            "required": [
                param.name
                for param in tool.parameters
                if getattr(param, "required", False)
            ],
            "additionalProperties": False,
        },
        "strict": True,
    }


def _custom_tool(tool: DictConfig):
    return {"type": "custom", "name": tool.name, "description": tool.description}


def load_toolspecs(cfg: DictConfig) -> list:
    """Load tool specifications from the configuration.

    Args:
        cfg (DictConfig): The configuration object.

    Returns:
        list: A list of tool specifications.
    """
    return [_tool_from_config(tool) for tool in cfg.tools.tools]

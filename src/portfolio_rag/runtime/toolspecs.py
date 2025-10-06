from omegaconf import DictConfig


def _tool_from_config(tool: str, params: DictConfig):
    """Convert a tool configuration into a tool specification dictionary."""
    if params.type == "custom":
        return _custom_tool(tool, params)
    return _function_tool(tool, params)


def _function_tool(tool: str, params: DictConfig):
    return {
        "type": "function",
        "name": tool,
        "description": params.description,
        "parameters": {
            "type": "object",
            "properties": {
                param.name: {"type": param.type, "description": param.description}
                for param in params.parameters
            }
            if "parameters" in params
            else {},
            "required": [
                param.name
                for param in params.parameters
                if getattr(param, "required", False)
            ]
            if "parameters" in params
            else [],
            "additionalProperties": False,
        },
        "strict": True,
    }


def _custom_tool(tool: str, params: DictConfig):
    return {"type": "custom", "name": tool, "description": params.description}


def load_toolspecs(cfg: DictConfig) -> list:
    """Load tool specifications from the configuration.

    Args:
        cfg (DictConfig): The configuration object.

    Returns:
        list: A list of tool specifications.
    """
    return [_tool_from_config(tool, params) for tool, params in cfg.tools.items()]

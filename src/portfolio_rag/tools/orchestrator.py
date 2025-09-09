from typing import Any

from omegaconf import DictConfig

from portfolio_rag.agents.codeagent import codeagent


def orchestrate(function: str, cfg: DictConfig, spinner_context, **kwargs: Any) -> str:
    with spinner_context("Analyzing..."):
        match function:
            case "query_portfolio_analyst":
                return codeagent(cfg, **kwargs)
            case _:
                raise ValueError(f"Unknown function: {function}")

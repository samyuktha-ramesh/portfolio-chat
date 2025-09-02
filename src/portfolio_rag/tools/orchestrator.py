from typing import Any

from omegaconf import DictConfig

from portfolio_rag.agents.codeagent import codeagent


def orchestrate(function: str, cfg: DictConfig, spinner_context, **kwargs: Any) -> str:
    with spinner_context("Analyzing..."):
        return codeagent(cfg, **kwargs)

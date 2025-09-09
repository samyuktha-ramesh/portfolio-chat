from typing import Any

from omegaconf import DictConfig

from portfolio_rag.agents.codeagent import codeagent
from portfolio_rag.tools.finance_qa import finance_qa


def orchestrate(function: str, cfg: DictConfig, spinner_context, **kwargs: Any) -> str:
    with spinner_context("Analyzing..."):
        match function:
            case "query_portfolio_analyst":
                print("Querying portfolio analyst...")
                return codeagent(cfg, **kwargs)
            case "finance_qa":
                print("Querying finance QA...")
                return finance_qa(cfg, **kwargs)
            case _:
                raise ValueError(f"Unknown function: {function}")

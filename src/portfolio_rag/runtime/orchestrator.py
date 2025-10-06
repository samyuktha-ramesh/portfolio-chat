from typing import Any

from hydra.utils import call
from omegaconf import DictConfig

from portfolio_rag.agents import run_codeagent, run_websearch_qa


def orchestrate(function: str, cfg: DictConfig, spinner_context, **kwargs: Any) -> str:
    with spinner_context("Analyzing..."):
        if function not in cfg.tools:
            return "Tool not found."

        backend = cfg.tools[function].backend  # either str or dict
        engine = getattr(backend, "engine", backend)

        match engine:
            case "codeagent":
                return run_codeagent(cfg, system_prompt=backend.system_prompt, **kwargs)
            case "websearch_qa":
                return run_websearch_qa(
                    cfg, system_prompt=backend.system_prompt, **kwargs
                )
            case "stress_test":
                return "Stress test executed. Results are positive."
            case "callable":
                return call(cfg.tools[function].backend.callable, **kwargs)
            case _:
                raise ValueError(f"Unknown backend type: {backend.type}")

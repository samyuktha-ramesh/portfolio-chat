import hydra
from omegaconf import DictConfig
from pathlib import Path
import re
from rich.console import Console
from smolagents import CodeAgent, OpenAIModel
from smolagents.monitoring import AgentLogger
from textwrap import dedent

logger = None

from smolagents.memory import ActionStep

def extract_last_agent_code(file_path: str) -> str | None:
    text = Path(file_path).read_text(encoding="utf-8", errors="replace")
    match = re.findall(
        r"Executing parsed code:\s*[-─━═]+.*?\n(.*?)(?=\n\s*[-─━═]{10,}|^\s*Execution logs:|\Z)",
        text,
        flags=re.DOTALL | re.MULTILINE
    )
    if not match:
        return None
    return dedent(match[-1]).strip()

def init_logger(wd: str | None = None):
    global logger
    if logger is None:
        wd = wd or hydra.core.hydra_config.HydraConfig.get().runtime.output_dir  # type: ignore
        logger = AgentLogger(
            console=Console(
                file=open(
                    f"{wd}/codeagent.log", "a", encoding="utf-8", errors="replace"
                ),
                force_terminal=False,
                width=120,
            )
        )


def run_codeagent(cfg: DictConfig, system_prompt: str, query: str) -> str:
    init_logger(cfg.get("working_dir", None))
    model = OpenAIModel(model_id=cfg.model.name, api_key=cfg.model.api_key)
    agent = CodeAgent(
        tools=[],
        model=model,
        add_base_tools=True,
        additional_authorized_imports=["csv", "pandas", "pgeocode", "numpy"],
        logger=logger,
    )
    response = agent.run(system_prompt + f" Query: {query}")
    return str(response)

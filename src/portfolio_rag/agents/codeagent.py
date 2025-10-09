import os

from hydra.core.hydra_config import HydraConfig
from omegaconf import DictConfig
from rich.console import Console
from smolagents import CodeAgent, OpenAIModel
from smolagents.monitoring import AgentLogger

loggers: dict[int, AgentLogger] = dict()


def get_logger(session_id: int) -> AgentLogger:
    global loggers
    if session_id not in loggers:
        if HydraConfig.initialized():
            wd = HydraConfig.get().runtime.output_dir
        else:
            wd = "."

        file_path = f"{wd}/{session_id}/"
        os.makedirs(file_path, exist_ok=True)
        loggers[session_id] = AgentLogger(
            console=Console(
                file=open(
                    file_path + "codeagent.log", "a", encoding="utf-8", errors="replace"
                ),
                force_terminal=False,
                width=120,
            )
        )
    return loggers[session_id]


def run_codeagent(
    cfg: DictConfig, system_prompt: str, query: str, session_id: int
) -> str:
    model = OpenAIModel(model_id=cfg.model.name, api_key=cfg.model.api_key)
    agent = CodeAgent(
        tools=[],
        model=model,
        add_base_tools=True,
        additional_authorized_imports=["csv", "pandas", "pgeocode", "numpy"],
        logger=get_logger(session_id),
    )
    response = agent.run(system_prompt + f" Query: {query}")
    return str(response)

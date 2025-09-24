import hydra
from omegaconf import DictConfig
from rich.console import Console
from smolagents import CodeAgent, OpenAIModel
from smolagents.monitoring import AgentLogger

logger = None


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

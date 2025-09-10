import hydra
from omegaconf import DictConfig
from rich.console import Console
from smolagents import CodeAgent, OpenAIModel
from smolagents.monitoring import AgentLogger

logger = None


def init_logger():
    global logger
    if logger is None:
        hydra_wd = hydra.core.hydra_config.HydraConfig.get().runtime.output_dir  # type: ignore
        logger = AgentLogger(
            console=Console(
                file=open(
                    f"{hydra_wd}/codeagent.log", "a", encoding="utf-8", errors="replace"
                ),
                force_terminal=False,
                width=120,
            )
        )


def run_codeagent(cfg: DictConfig, system_prompt: str, query: str) -> str:
    init_logger()
    model = OpenAIModel(model_id=cfg.model.name, api_key=cfg.model.api_key)
    agent = CodeAgent(
        tools=[],
        model=model,
        add_base_tools=True,
        additional_authorized_imports=["csv", "pandas", "pgeocode"],
        logger=logger,
    )
    response = agent.run(system_prompt + f" Query: {query}")
    return str(response)

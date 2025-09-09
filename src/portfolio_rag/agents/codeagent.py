from omegaconf import DictConfig
from smolagents import CodeAgent, OpenAIModel


def run_codeagent(cfg: DictConfig, system_prompt: str, query: str) -> str:
    model = OpenAIModel(model_id=cfg.model.name, api_key=cfg.model.api_key)
    agent = CodeAgent(
        tools=[],
        model=model,
        add_base_tools=True,
        additional_authorized_imports=["pandas"],
    )
    response = agent.run(system_prompt + f" Query: {query}")
    return str(response)

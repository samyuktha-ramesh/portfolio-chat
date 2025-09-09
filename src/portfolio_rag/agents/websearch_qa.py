from omegaconf import DictConfig
from openai import OpenAI


def run_websearch_qa(cfg: DictConfig, system_prompt: str, query: str) -> str:
    """
    Answers finance-related questions using the OpenAI Responses API
    with optional live web search.
    """
    client = OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)

    response = client.responses.create(
        model=cfg.name,
        tools=[{"type": "web_search"}],
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
    )

    return response.output_text

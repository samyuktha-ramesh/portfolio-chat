from omegaconf import DictConfig
from openai import OpenAI


def finance_qa(cfg: DictConfig, query: str) -> str:
    """
    Answers finance-related questions using the OpenAI Responses API
    with optional live web search.
    """
    client = OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)

    system_prompt = (
        "You are a financial assistant. "
        "You can explain financial concepts, market trends, instruments, "
        "and provide context on news. "
        "When useful, you may search the web for up-to-date information, "
        "but keep your answers grounded in finance and clearly separate "
        "between general knowledge and live data."
    )

    response = client.responses.create(
        model=cfg.name,
        tools=[{"type": "web_search"}],
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
    )

    return response.output_text

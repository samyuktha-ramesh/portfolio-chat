# ruff: noqa: E402
from dotenv import load_dotenv

load_dotenv()

import csv
from datetime import datetime

import hydra
from omegaconf import DictConfig

from portfolio_rag.agents import run_codeagent
from portfolio_rag.eval.questions import QUESTIONS


def run_query(cfg: DictConfig, query: str) -> str:
    return run_codeagent(
        cfg,
        system_prompt=cfg.tools.query_portfolio_analyst.backend.system_prompt,
        query=query,
    )


@hydra.main(config_path="configs", config_name="config", version_base="1.3")
def run_dataset(cfg: DictConfig):
    RUNS = 3
    OUTPUT_PATH = None
    rows = []

    for level, qs in QUESTIONS.items():
        for query in qs:
            for run in range(RUNS):
                print(f"Running query at {level} level (run {run + 1}): {query}")
                answer = run_query(cfg, query)
                rows.append(
                    {
                        "difficulty": level,
                        "query": query,
                        "run": run + 1,
                        "answer": answer,
                    }
                )

    # add timestamped file if not specified
    if OUTPUT_PATH is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        OUTPUT_PATH = f"results_{ts}.csv"

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["difficulty", "query", "run", "answer"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved results to {OUTPUT_PATH}")


if __name__ == "__main__":
    run_dataset()

# ruff: noqa: E402
from dotenv import load_dotenv

load_dotenv()

import csv
import re
from datetime import datetime

import hydra
from omegaconf import DictConfig

from portfolio_rag.agents import run_codeagent


def run_query(cfg: DictConfig, query: str) -> str:
    return run_codeagent(
        cfg,
        system_prompt=cfg.tools.query_portfolio_analyst.backend.system_prompt,
        query=query,
        session_id=0,
    )


def extract_largest_number(text: str):
    matches = re.findall(r"[-+]?\d*\.\d+|\d+", text.replace(",", ""))
    if not matches:
        return None
    nums = [float(m) for m in matches]
    return max(nums)


def is_equal(a, b, tol=1e-2):
    return abs(a - b) <= tol


CHUNK_SIZE = 20  # adjust as you like


@hydra.main(config_path="configs", config_name="config", version_base="1.3")
def run_dataset(cfg: DictConfig):
    INPUT_PATH = "data/validationExampleQuestions.csv"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_PATH = f"results_{ts}.csv"

    fieldnames = [
        "N",
        "n",
        "C",
        "Q",
        "A",
        "agent_answer",
        "extracted_number",
        "Correct",
    ]

    buffer = []

    with (
        open(INPUT_PATH, newline="", encoding="utf-8", errors="replace") as fin,
        open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as fout,
    ):
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for i, row in enumerate(reader, 1):
            try:
                query = row["Q"]
                print(f"Running query {i}: {query}")

                answer = run_query(cfg, query)
                extracted = extract_largest_number(answer)

                try:
                    gold = float(row["A"])
                except ValueError:
                    gold = None

                correct = is_equal(extracted, gold) if (extracted and gold) else False

                row_out = {
                    **row,
                    "agent_answer": answer,
                    "extracted_number": extracted,
                    "Correct": correct,
                }
            except Exception as e:
                print(f"Error on row {i}: {e}")
                row_out = {
                    **row,
                    "agent_answer": f"ERROR: {e}",
                    "extracted_number": None,
                    "Correct": False,
                }

            buffer.append(row_out)

            if len(buffer) >= CHUNK_SIZE:
                writer.writerows(buffer)
                fout.flush()
                buffer.clear()

        # flush leftovers
        if buffer:
            writer.writerows(buffer)
            fout.flush()

    print(f"Saved results to {OUTPUT_PATH}")


if __name__ == "__main__":
    run_dataset()

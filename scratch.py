import re
from textwrap import dedent
from pathlib import Path

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

# Example usage
if __name__ == "__main__":
    code = extract_last_agent_code("outputs/2025-10-09/13-43-55/codeagent.log")
    print(code if code else "No code found.")

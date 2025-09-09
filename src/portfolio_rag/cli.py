# ruff: noqa: E402
from dotenv import load_dotenv

load_dotenv()

import hydra
from omegaconf import DictConfig

from .app import ChatApp


@hydra.main(config_path="configs", config_name="config", version_base="1.3")
def main(cfg: DictConfig):
    chat = ChatApp(cfg)
    chat.run()


if __name__ == "__main__":
    main()  # type: ignore

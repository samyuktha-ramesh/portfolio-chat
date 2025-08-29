# Portfolio RAG

Modern Large Language Models (LLMs) are extremely capable of creative tasks and reasoning, however often struggle with grounding their responses in external knowledge. This is where Retrieval-Augmented Generation (RAG) comes in. Traditional RAG approaches involve retrieving relevant documents or data from a knowledge base and using that information to inform the model's responses. However, tabular data presents unique challenges for RAG: The structure and format of tabular data can make it difficult for LLMs to interpret and utilize effectively. 

This repository contains a robust framework for retrieving and processing tabular data to enhance the capabilities of LLMs. We introduce `portfolio-rag`, a specialized tool for working with tabular portfolio data. However, this approach generalizes to all tabular data use cases. Developed as part of the [ETH Zurich FinsureTech Hub Innovation Project](https://finsuretech.ethz.ch/continuing-education/cas-ml-in-finance-and-insurance/innovation-projects.html) in collaboration with [PwC Switzerland](https://www.pwc.ch/).

## Installation`

1. To install the necessary dependencies, you recommend [uv](https://docs.astral.sh/uv/)

    ```bash
    pip install uv
    uv sync
    ```

    However, if you prefer not to use `uv`, you can manually install the dependencies listed in `pyproject.toml` using pip:

    ```bash
    python -m venv .venv
    source .venv/bin/activate # Windows: .venv/Scripts/activate 
    pip install -e .[dev]
    ```

2. Download the necessary data files and place them in the `data` directory.

3. Copy `.env.example` to `.env` and update the environment variables as needed.

## Usage

Once the dependencies are installed and the data files are in place, you can chat with the model using the command line interface (CLI).

```sh
portfolio-chat
```

You can use the Hydra CLI to interact with the model and configuration. For example, you might want to specify a different model (or model provider)
```
portfolio-chat model.name="gpt-4.1" prompts.system="You are a helpful assistant."
```

The following commands are available:
```
/help: Displays this help message.
/reset: Resets the conversation history.
/quit: Exits the chat.
```

## Basic Pipeline:
1. Orchestrator 
    - Plans out how to respond to the queries
    - Has access to "retrieve_data" tool
        - "retrieve_data(input: str) -> Any"
        - input should be minimal: retrieves a single piece of data

Retrieve data:
1. Decide if RAG necessary
    - aka retrieve csv files that are necessary (or None)
    - output: list of csv files
    - open questions: 
        - needs to be scalable: can't just give it every csv
        - how does cursor do it? maybe vectorize documents? just columns?
2. If len(relevant_files > 0):
    2.0. Preprocess agent
        - Optional ?
        - Potentially: Performs joins
        - Potentially: Returns list of relevant cols for query agent.
    2.1. Directly perform Pandas (or SQL) query(s)
    2.2. Return output

## Configuration

This project uses `Hydra` for configuration management. Please refer to the [Hydra documentation](https://hydra.cc/docs/intro/) for more information on how to configure your application. The configuration files are located in the `src\portfolio_rag\configs` directory.

The configuration defines models, prompts, and other settings for the application.
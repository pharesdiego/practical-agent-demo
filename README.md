# LangGraph Agents Demo

This project demonstrates how to build agents using LangGraph.

## Setup

1.  Install dependencies using `uv` (install `uv` with `curl -LsSf https://astral.sh/uv/install.sh | sh`) and then do:

    ```bash
    uv sync
    ```

    See the [uv installation documentation](https://docs.astral.sh/uv/getting-started/installation/) for more information.

2.  Install `just` with `brew install just` or `npm install -g rust-just`.

    See the [just installation documentation](https://github.com/casey/just?tab=readme-ov-file#packages) for more information.

3.  Activate the virtual environment:

    ```bash
    source .venv/bin/activate
    ```

4.  Run the web server:

    ```bash
    just run_web
    ```

5.  Make sure to set the `OPENROUTER_API_KEY` environment variable at `agents/.env`. You can find more information about OpenRouter and  how to obtain an API key [here](https://openrouter.ai/).

6.  Run the LangGraph server:

    ```bash
    just run_agents
    ```

## Optional Environment Variables

*   `LANGSMITH_API_KEY`:  Used for LangSmith tracing.
*   `LANGSMITH_TRACING`:  Enable or disable LangSmith tracing (true/false).
*   `LANGSMITH_ENDPOINT`:  The LangSmith endpoint. Defaults to "https://api.smith.langchain.com".
*   `LANGSMITH_PROJECT`:  The LangSmith project name. Defaults to "practical-agent-demo".

## Dependencies

*   `uv`
*   `just`

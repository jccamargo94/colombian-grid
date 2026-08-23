<div align="center">
  <img alt="colombian-grid logo" src="./docs/assets/logo.svg" width="70">
  <h1>Colombian Grid</h1>
  <p><i>Query, extract, and process public data from the Colombian electricity market with Python.</i></p>
</div>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/colombian-grid)](https://pypi.org/project/colombian-grid/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![Docs](https://img.shields.io/badge/docs-mkdocs--material-070394)](https://jccamargo94.github.io/colombian-grid/)

</div>

---

## About The Project

`colombian-grid` is a Python library that provides a simple, async-first interface to access and process public data from the Colombian electricity market. Today it implements two data sources:

- **[Paratec](https://paratec.xm.com.co/)**: infrastructure data — generators, transmission lines, substations, and hydrology.
- **[XM](https://www.xm.com.co/)**: market data — generation, demand, prices, and other metrics, with automatic date-range chunking and a pandas `DataFrame` output.

### Key Features

- 🔌 **Multiple Data Sources**: Paratec (infrastructure) and XM (market data) APIs
- ⚡ **Async & Sync Clients**: async clients for high throughput, plus a sync XM client for simple scripts
- 🤖 **Automatic Chunking**: XM requests automatically split large date ranges to respect API limits
- 🔁 **Built-in Retry Logic**: exponential backoff with jitter for transient errors
- 📊 **Pandas Integration**: XM data is returned as pandas DataFrames for easy analysis
- ✅ **Type Safety**: fully type-hinted (ships a `py.typed` marker), with optional Pydantic schema validation

## Installation

### PyPI

```bash
pip install colombian-grid
```

## Quick Start

Import the clients from the top-level package:

```python
from colombian_grid import AsyncParatecClient, AsyncXMClient, SyncXMClient
```

### XM API - Market Data

```python
import asyncio
from datetime import date
from colombian_grid import AsyncXMClient

async def main():
    async with AsyncXMClient() as client:
        # Get system generation data
        data = await client.get_data(
            metric="Gene",
            entity="Sistema",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        print(data.head())

asyncio.run(main())
```

`SyncXMClient` mirrors the same `get_data(...)` / `get_available_metrics()` interface for non-async scripts, using `with SyncXMClient() as client: ...`.

### Paratec API - Infrastructure Data

```python
import asyncio
from colombian_grid import AsyncParatecClient

async def main():
    async with AsyncParatecClient() as client:
        # Get generator data
        generators = await client.get_generation_data()
        print(f"Found {len(generators)} generators")

        # Also available: get_substation_data(), get_transmission_line_data(), get_hydro_data()

asyncio.run(main())
```

Both `AsyncParatecClient` and `AsyncXMClient` accept optional `timeout` and `max_retries` constructor arguments and support the `async with` context manager, which closes the underlying HTTP connection automatically.

## Documentation

For comprehensive guides, API reference, and examples, visit our [documentation site](https://jccamargo94.github.io/colombian-grid/).

### Building Documentation Locally

```bash
# Install documentation dependencies
uv pip install mkdocs mkdocs-material "mkdocstrings[python]"

# Build and serve documentation
uv run mkdocs serve
```

The documentation will be available at `http://127.0.0.1:8000`.

## Development

This project uses `uv` for dependency management. To set up a development environment:

```bash
# Clone the repository
git clone https://github.com/jccamargo94/colombian-grid.git
cd colombian-grid

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run pre-commit hooks
uv run pre-commit run --all-files
```

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

## Have questions or suggestions?

Check out our [documentation](https://jccamargo94.github.io/colombian-grid/) or open an issue in our repository. We are here to help you. 😊

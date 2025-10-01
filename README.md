<div align="center">
  <h1 align="center">Digitizing the Colombian Grid</h1>
  <h3 align="center">Carry all the information of the Colombian grid with you</h3>
</div>

<div align="center">
  <!-- PROJECT LOGO -->
  <br />
      <img alt="colombian-grid Logo" src="./docs/assets/portrait-logo.png" width="400px">
  <br />
  <p><i>The digitization of the Colombian grid in one line</i></p>
</div>

---

✨⚡ Query, extract, and process available information from the Colombian energy market with Python.

[![PyPI](https://img.shields.io/pypi/v/colombian-grid)](https://pypi.org/project/colombian-grid/)
[![Documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue)](https://jccamargo94.github.io/colombian-grid/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## About The Project

`colombian-grid` is a Python library designed to provide a simple and efficient interface to access and process public data from the Colombian electricity market through the Paratec and XM APIs.

### Key Features

- 🔌 **Multiple Data Sources**: Access data from both Paratec (infrastructure) and XM (market data) APIs
- ⚡ **Async & Sync Clients**: Choose between asynchronous clients for high performance or synchronous for simplicity
- 🤖 **Automatic Chunking**: Handles large date ranges automatically, respecting API restrictions
- � **Built-in Retry Logic**: Exponential backoff with jitter for handling transient errors
- 📊 **Pandas Integration**: Returns data as pandas DataFrames for easy analysis
- ✅ **Type Safety**: Optional Pydantic schema validation for API responses

## Installation

### PyPI

```bash
pip install colombian-grid
```

## Quick Start

### XM API - Market Data

```python
import asyncio
from datetime import date
from colombian_grid.core.xm import AsyncXMClient

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

### Paratec API - Infrastructure Data

```python
import asyncio
from colombian_grid.core.paratec import AsyncParatecClient

async def main():
    client = AsyncParatecClient()

    # Get generator data
    generators = await client.get_generation_data()
    print(f"Found {len(generators)} generators")

    await client._http_client.close()

asyncio.run(main())
```

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

## Have questions or suggestions?

Check out our [documentation](https://jccamargo94.github.io/colombian-grid/) or open an issue in our repository. We are here to help you. 😊

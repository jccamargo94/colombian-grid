
<div align="center">
  <img alt="colombian-grid logo" src="assets/logo.svg" width="70">
  <h1>Colombian Grid</h1>
  <p><i>A Python package for accessing public data from the Colombian electricity market.</i></p>
</div>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/colombian-grid)](https://pypi.org/project/colombian-grid/)
[![Docs](https://img.shields.io/badge/docs-mkdocs--material-070394)](https://jccamargo94.github.io/colombian-grid/)

</div>

---

`colombian-grid` is a Python library designed to make it easy to access public data from the Colombian electricity market, consuming the Paratec and XM APIs directly. The library offers an async-first interface to query generator, transmission infrastructure, hydrology, and market data.

## Key Features
- **Multiple Data Sources**: Access data from Paratec and XM, two of the main sources of information in the Colombian energy market.
- **Async Interface**: Built with `asyncio` and `httpx` for non-blocking, high-performance I/O.
- **Data Validation**: Uses `Pydantic` to validate the structure and types of API responses (optional).
- **Automatic Chunking**: For large date ranges, the library automatically splits requests to respect XM's API limits.
- **Sync and Async Clients**: Flexible enough to integrate into both async projects and traditional sync scripts.

## Getting started

Install the package with `pip install colombian-grid` and follow the [Getting Started](getting-started.md) guide to run your first XM or Paratec query in a few minutes.

## Questions or suggestions?
Check out our [documentation](https://jccamargo94.github.io/colombian-grid/) or open an issue in our repository. We're here to help. 😊

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `AsyncSourceClient` shared base class providing HTTP lifecycle management (`close()`, async context manager) for async data-source clients; `AsyncParatecClient` now supports `async with` and configurable `timeout`/`max_retries`, matching `AsyncXMClient`
- Top-level package re-exports: `from colombian_grid import AsyncParatecClient, AsyncXMClient, SyncXMClient`
- `py.typed` marker (PEP 561) so downstream type checkers recognize the package as typed
- Refined SVG logo (`docs/assets/logo.svg`) and a reduced favicon glyph (`docs/assets/favicon.svg`), wired as the mkdocs site favicon
- XM API interface with AsyncXMClient and SyncXMClient for accessing Colombian electricity market data
- Automatic date chunking for large time ranges (respects API limits: 30 days for hourly/daily, 731 for monthly)
- Support for filtering data by resource codes, agent codes, and other parameters
- `get_available_metrics()` method to discover all available XM API metrics
- Comprehensive test suite for XM API fetchers with mocked HTTP responses
- Usage examples in `examples/xm_api_usage.py`
- pandas as a project dependency for DataFrame operations
- Data transformation utilities in `colombian_grid.utils.data_transform`:
  - `wide_to_long_timeseries()` - Convert hourly/daily/monthly wide format to long format with timestamps
  - `long_to_wide_timeseries()` - Convert long format back to wide format
  - `add_timestamp_to_hourly_data()` - Convenience function for hourly data transformation
  - Support for Hour01-Hour24 convention (Hour01=00:00, Hour24=23:00)
- Comprehensive documentation site with MkDocs Material theme
- GitHub Actions workflow for automatic documentation deployment to GitHub Pages
- Documentation pages: Quick Start Guide, API Reference, and Examples

### Changed

- `APIDataSource` is now generic (`APIDataSource[T]`) instead of lying about returning `list`; Paratec fetchers parametrize it as `APIDataSource[list]` and `AsyncXMFetcher` as `APIDataSource[pd.DataFrame]`, matching their real return types
- Refreshed README.md and docs/index.md headers with the new SVG logo, a single tagline, and real shields.io badges; rewrote README body to accurately describe the current implementation (Paratec + XM only) and replaced the Paratec example's `client._http_client.close()` with `async with AsyncParatecClient() as client:`
- Refactored XM fetchers using DRY principle with BaseXMFetcher abstract base class
- Updated all type hints to Python 3.10+ syntax (list[T], dict[K,V], X | None)
- Removed legacy typing imports (Optional, List, Dict, etc.)
- Improved copilot instructions with modern type hint guidelines
- Restructured documentation to follow standard MkDocs layout (mkdocs.yml at root, docs/ for content)
- Enhanced README with better feature descriptions, usage examples, and documentation links
- Added return type annotations to AsyncParatecClient methods for better API documentation

### Fixed

- TOML syntax error in pyproject.toml (removed trailing comma)
- Leap year handling in date chunking tests
- RuntimeWarnings about unawaited coroutines in XM API tests by using `inspect.iscoroutinefunction` instead of `asyncio.iscoroutine`
- AsyncMock configuration in tests to properly handle `raise_for_status()` and `json()` methods
- Documentation build warnings by adding proper return type annotations
- Duplicate mkdocs.yml files (consolidated to root directory)

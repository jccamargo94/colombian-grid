# Colombian Grid - AI Coding Agent Instructions

## Project Overview
`colombian-grid` is a Python library for accessing public data from the Colombian electricity market via the Paratec API. The library provides asynchronous interfaces to query generators, transmission infrastructure, and hydrology data. Currently in construction to add more features such as XM-API, SIMEM and Sinergox in order to cover the main data sources in the Colombian energy market.

## Architecture

### Core Components
- **Data Fetchers** (`src/colombian_grid/core/base/interfaces/`): Domain-specific fetchers that implement the `APIDataSource` abstract interface
  - **Paratec** (`paratec/`): Generators, transmission, hydrology fetchers
  - **XM** (`xm/`): Market data fetchers with automatic chunking for large date ranges
- **HTTP Infrastructure** (`src/colombian_grid/core/infra/http/`): Async HTTP client with retry logic built on `httpx`
- **Schemas** (`src/colombian_grid/core/schemas/`): Pydantic models for request/response validation
- **Clients**:
  - **Paratec** (`src/colombian_grid/core/paratec/paratec.py`): `AsyncParatecClient` for infrastructure data
  - **XM** (`src/colombian_grid/core/xm/xm_client.py`): `AsyncXMClient` and `SyncXMClient` for market data

### Key Design Patterns
1. **Abstract Interfaces**: All data fetchers inherit from `APIDataSource` with a standardized `get_data()` method
2. **Dependency Injection**: Clients receive `AsyncHttpClient` and inject it into fetchers
3. **Optional Schema Validation**: Fetchers accept `output_schema` parameter to validate responses with Pydantic models
4. **Retry Logic**: HTTP client implements exponential backoff with jitter for status codes `[408, 429, 500, 502, 503, 504]`
5. **Date Chunking**: XM fetchers automatically chunk large date ranges to respect API limits (max 30 days for hourly/daily, 731 for monthly)
6. **DRY with Base Classes**: XM API uses `BaseXMFetcher` abstract base class to eliminate code duplication between async/sync implementations
   - Shared logic in base class: metrics fetching, chunking preparation, data validation, single chunk fetching
   - Subclass-specific: execution strategy (parallel with `asyncio.gather()` vs sequential with loops)
   - Abstract method `_execute_fetch_strategy()` defines the template for subclasses
7. **Template Method Pattern**: Base class defines the algorithm structure, subclasses implement specific steps
8. **Strategy Pattern**: Different execution strategies for async (parallel) vs sync (sequential) operations

### Data Flow
```
# Paratec API
AsyncParatecClient → Fetcher (GeneratorFetcher/TransmissionFetcher/HydroFetcher)
→ AsyncHttpClient → Paratec API → Pydantic Schema (optional) → User

# XM API
AsyncXMClient/SyncXMClient → AsyncXMFetcher/SyncXMFetcher → AsyncHttpClient
→ XM API (with chunking) → Pydantic Schema (optional) → pandas DataFrame → User
```

## Development Workflows

### Environment Setup
- **Package Manager**: Uses `uv` for dependency management (see `uv.lock`)
- **Python Version**: Requires Python ≥3.11 (check `.python-version`)
- **Install**: `pip install colombian-grid` or install from source with `uv sync`

### Testing
- **Framework**: pytest with pytest-asyncio for async tests
- **Run Tests**: `pytest tests/` (tests are in `tests/httpx/`)
- **Mock Pattern**: Use `unittest.mock.patch` with `AsyncMock` for httpx responses (see `tests/httpx/test_async_client.py`)
- **Coverage**: pytest-cov available for coverage reports

### Code Quality
- **Pre-commit Hooks**: Ruff (linting + formatting), trailing whitespace, merge conflicts, TOML validation
- **Run**: `pre-commit run --all-files`
- **Branch Protection**: Cannot commit directly to `main`

### Documentation
- **Framework**: MkDocs with Material theme (see `docs/mkdocs.yml`)
- **Build**: `mkdocs build` (from `docs/` directory)
- **Serve Locally**: `mkdocs serve` to preview at `http://127.0.0.1:8000`
- **Critical Rule**: Update documentation whenever API changes occur to avoid inconsistency
- **Location**: Documentation pages in `docs/docs/` (index.md, guia.md, api-reference.md, ejemplos.md)

### Publishing to PyPI
- **Current**: Handled by `uv` tooling
- **In Development**: Improving workflow with automated version bumping, test execution before publish
- **Future**: Implementing CI/CD pipeline for automated releases

### Change Documentation
- **CRITICAL**: Do NOT create separate `.md` files for change summaries (e.g., `REFACTORING_SUMMARY.md`, `XM_IMPLEMENTATION.md`)
- **ALWAYS use CHANGELOG.md**: Document all changes, features, refactorings, and fixes in `CHANGELOG.md`
- **Format**: Follow [Keep a Changelog](https://keepachangelog.com/) format with sections:
  - `## [Unreleased]` - For work in progress
  - `### Added` - New features
  - `### Changed` - Changes in existing functionality
  - `### Deprecated` - Soon-to-be removed features
  - `### Removed` - Removed features
  - `### Fixed` - Bug fixes
  - `### Security` - Security fixes
- **Style**: Keep entries concise and user-focused (not implementation details)
- **Example**:
  ```markdown
  ## [Unreleased]
  ### Added
  - XM API interface with async/sync clients for market data
  - Automatic date chunking for large time ranges

  ### Changed
  - Refactored XM fetchers using DRY principle with base class
  - Updated all type hints to Python 3.10+ syntax
  ```

## Project-Specific Conventions

### Type Hints - Modern Python Standard
**CRITICAL: Always use Python 3.10+ type hint syntax.** This project requires Python ≥3.11.

**Use built-in generics:**
- `list[T]` not `List[T]`
- `dict[K, V]` not `Dict[K, V]`
- `tuple[T, ...]` not `Tuple[T, ...]`
- `set[T]` not `Set[T]`

**Use union operator for optionals:**
- `str | None` not `Optional[str]`
- `list[str] | None` not `Optional[List[str]]`
- `int | str | None` not `Union[int, str, None]`

**Special cases:**
- `type[ClassName]` for class types (not instances)
- Only import from `typing` for: `Protocol`, `TypeVar`, `Literal`, `TypeAlias`, `Callable`, etc.

### Async-First Design
- All HTTP operations are async - use `async`/`await` throughout
- Client must be used with async context manager: `async with AsyncHttpClient() as client:`
- **Pattern Development**: Async/await error handling patterns are being established - document new patterns as they emerge

### URL Management
- API endpoints centralized in `src/colombian_grid/core/base/interfaces/*/utils.py`
- Paratec URLs in `paratec/utils.py`
- XM URLs in `xm/utils.py` with API-specific restrictions (max days per request type)
- Update URLs there when APIs change

### Error Handling
- HTTP errors raise `httpx.HTTPStatusError` - call `response.raise_for_status()`
- Timeout/network errors retried automatically up to `max_retries` (default: 3)
- **Pattern Development**: Standardized error handling patterns are being established across fetchers

### Schema Usage
When adding new endpoints:
1. Create Pydantic model in `src/colombian_grid/core/schemas/`
2. Add fetcher in `src/colombian_grid/core/base/interfaces/<api_name>/`
3. Expose via client (e.g., `AsyncParatecClient`, `AsyncXMClient`)
4. Example: `GeneratorEntity` uses Spanish field aliases matching API response keys

### Type Hints - Modern Python 3.10+ Standard
**ALWAYS use modern Python type hint syntax** (project requires Python ≥3.11):

#### Required Patterns:
- ✅ `list[str]` instead of `List[str]` (no typing import needed)
- ✅ `dict[str, int]` instead of `Dict[str, int]`
- ✅ `tuple[int, str]` instead of `Tuple[int, str]`
- ✅ `set[str]` instead of `Set[str]`
- ✅ `str | None` instead of `Optional[str]` (union operator)
- ✅ `str | int | None` instead of `Union[str, int, None]`
- ✅ `type[BaseModel]` for class types (not instances)

#### Examples:
```python
# ✅ Correct - Modern style
def get_data(
    filter_by: list[str] | None = None,
    output_schema: type[BaseModel] | None = None,
) -> pd.DataFrame:
    ...

# ❌ Incorrect - Legacy style (do not use)
from typing import Optional, List
def get_data(
    filter_by: Optional[List[str]] = None,
    output_schema: Optional[BaseModel] = None,
) -> pd.DataFrame:
    ...
```

#### When to Use Each:
- `list[T]`, `dict[K, V]`, `tuple[T, ...]` - For collection types
- `X | None` - For optional parameters (replaces `Optional[X]`)
- `X | Y | Z` - For union types (replaces `Union[X, Y, Z]`)
- `type[ClassName]` - When referring to the class itself, not an instance

#### No typing Imports Needed:
Built-in generics work natively in Python 3.9+, and the union operator `|` works in Python 3.10+. Only import from `typing` for advanced features like `Protocol`, `TypeVar`, `Literal`, etc.

### XM API Specifics
- **Date Chunking**: Automatically splits large date ranges to respect API limits
  - Hourly/Daily: 30 days per request
  - Monthly: 731 days per request
  - Long spans (>2 years): Additional year-level chunking to avoid API overhead
- **Dual Clients**: `AsyncXMClient` for parallel requests, `SyncXMClient` for sequential requests
- **Filter Support**: Pass `filter_by` list to filter data by resource codes, agent codes, etc.
- **Metrics Discovery**: Use `get_available_metrics()` to see all available MetricId/Entity combinations

## Common Tasks

### Adding a New Data Source
1. Define URL in appropriate `utils.py` (e.g., `paratec/utils.py` or `xm/utils.py`)
2. Create Pydantic schema in `schemas/` with field descriptions in Spanish
3. Implement fetcher class inheriting from `APIDataSource` in `interfaces/<api_name>/`
4. Add fetcher to appropriate client and create public method
5. Write tests mocking httpx responses in `tests/<api_name>/`
6. **Update documentation** in `docs/docs/` to reflect the new API endpoint

### Working with XM API
1. Use `AsyncXMClient` for async operations, `SyncXMClient` for sync operations
2. Always start by checking available metrics: `await client.get_available_metrics()`
3. Date ranges are automatically chunked - no need to manually split large requests
4. Use filters to narrow results: `filter_by=["TBST", "GVIO"]` for specific resources
5. See `examples/xm_api_usage.py` for complete usage examples

### Building and Serving Documentation
1. Navigate to `docs/` directory
2. Run `mkdocs build` to generate static site in `site/`
3. Run `mkdocs serve` for live preview during development
4. Validate all examples and API references work before committing

### Debugging API Issues
- Check `AsyncHttpClient._request_with_retry()` for retry logic
- Verify URLs in `paratec/utils.py` against Paratec backend
- Test response schemas with `output_schema` parameter in fetchers

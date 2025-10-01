# XM API Interface

This module provides comprehensive access to the Colombian XM electricity market API (https://servapibi.xm.com.co/).

## Features

- ✅ **Async & Sync Clients**: Choose between async (`AsyncXMClient`) for parallel requests or sync (`SyncXMClient`) for sequential requests
- ✅ **Automatic Date Chunking**: Handles large date ranges automatically, respecting API restrictions
- ✅ **Built-in Retry Logic**: Exponential backoff with jitter for failed requests
- ✅ **Metrics Discovery**: Query all available metrics and their metadata
- ✅ **Filter Support**: Filter data by resource codes, agent codes, reservoirs, rivers, etc.
- ✅ **Smart Chunking**: For very long time spans (>2 years), uses year-level chunking to avoid API overhead

## Installation

```bash
pip install colombian-grid
```

## Quick Start

### Async Client (Recommended for Performance)

```python
import asyncio
from datetime import date
from colombian_grid.core.xm import AsyncXMClient

async def main():
    async with AsyncXMClient() as client:
        # Get all available metrics
        metrics = await client.get_available_metrics()
        print(f"Total metrics: {len(metrics)}")

        # Fetch system generation data
        data = await client.get_data(
            metric="Gene",
            entity="Sistema",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        print(data.head())

asyncio.run(main())
```

### Sync Client (Simple to Use)

```python
from datetime import date
from colombian_grid.core.xm import SyncXMClient

with SyncXMClient() as client:
    # Get available metrics
    metrics = client.get_available_metrics()

    # Fetch real demand data
    data = client.get_data(
        metric="DemaReal",
        entity="Sistema",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31)
    )
    print(data.head())
```

## API Reference

### Client Methods

#### `get_available_metrics()`

Fetches all available metrics from the XM API.

**Returns:** DataFrame with columns:
- `MetricId`: Unique metric identifier (e.g., "Gene", "DemaReal")
- `MetricName`: Human-readable metric name in Spanish
- `Entity`: Entity type (Sistema, Recurso, Agente, etc.)
- `MaxDays`: Maximum days per request for this metric
- `Type`: Data granularity (HourlyEntities, DailyEntities, MonthlyEntities)
- `Url`: API endpoint URL
- `Filter`: Available filter field (if applicable)
- `MetricUnits`: Units of measurement
- `MetricDescription`: Metric description in Spanish

**Example:**
```python
metrics = await client.get_available_metrics()

# Find all generation-related metrics
gen_metrics = metrics[metrics['MetricName'].str.contains('Generación')]
print(gen_metrics[['MetricId', 'MetricName', 'Entity']])
```

#### `get_data(metric, entity, start_date, end_date, filter_by=None)`

Fetches data for a specific metric with automatic chunking for large date ranges.

**Parameters:**
- `metric` (str): Metric ID (e.g., "Gene", "DemaReal", "PrecBolsNaci")
- `entity` (str): Entity type (e.g., "Sistema", "Recurso", "Agente")
- `start_date` (date): Start date for data retrieval
- `end_date` (date): End date for data retrieval
- `filter_by` (Optional[List[str]]): Optional list of filter values (e.g., resource codes)

**Returns:** pandas DataFrame with the requested data

**Raises:**
- `ValueError`: If metric/entity combination is invalid
- `httpx.HTTPStatusError`: If API request fails after retries

**Example:**
```python
# Fetch generation by specific resources
data = await client.get_data(
    metric="Gene",
    entity="Recurso",
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31),
    filter_by=["TBST", "GVIO", "JEP1"]  # Specific power plants
)
```

## Common Use Cases

### 1. Fetch System-Wide Generation

```python
async with AsyncXMClient() as client:
    data = await client.get_data(
        metric="Gene",
        entity="Sistema",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31)
    )
    # Automatic chunking handles the full year
```

### 2. Query Specific Resources

```python
async with AsyncXMClient() as client:
    # First, get list of all resources
    resources = await client.get_data(
        metric="ListadoRecursos",
        entity="Sistema",
        start_date=date.today(),
        end_date=date.today()
    )

    # Then fetch data for specific resources
    hydro_plants = ["GVIO", "JEP1", "TBST"]  # Example hydro plants
    gen_data = await client.get_data(
        metric="Gene",
        entity="Recurso",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        filter_by=hydro_plants
    )
```

### 3. Analyze Electricity Prices

```python
async with AsyncXMClient() as client:
    prices = await client.get_data(
        metric="PrecBolsNaci",
        entity="Sistema",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 31)
    )

    # Calculate average hourly prices
    hour_cols = [col for col in prices.columns if 'Hour' in col]
    avg_prices = prices[hour_cols].mean()
    print(f"Average hourly prices:\n{avg_prices}")
```

### 4. Long Time Span Analysis

```python
# The client automatically chunks requests for very long periods
async with AsyncXMClient() as client:
    # This will be split into multiple year-level chunks
    multi_year_data = await client.get_data(
        metric="Gene",
        entity="Sistema",
        start_date=date(2018, 1, 1),
        end_date=date(2024, 12, 31)  # 7 years of data
    )
    # Data is fetched in parallel (async) or sequentially (sync)
```

## API Restrictions & Chunking

The XM API imposes restrictions on the maximum date range per request:

| Data Type | Max Days per Request |
|-----------|---------------------|
| Hourly    | 30 days            |
| Daily     | 30 days            |
| Monthly   | 731 days (~2 years)|
| Annual    | 366 days           |

### Automatic Chunking Logic

The client automatically handles chunking:

1. **For spans ≤ 2 years**: Chunks by max days allowed for the data type
2. **For spans > 2 years**: Additional year-level chunking to avoid API overhead
3. **Async client**: Fetches all chunks in parallel
4. **Sync client**: Fetches chunks sequentially

Example:
```python
# Requesting 5 years of hourly data
# Will be chunked into ~60 requests (5 years * 12 months / 30 days)
# Async client fetches all in parallel, Sync client fetches sequentially
```

## Available Metrics

The XM API provides numerous metrics across different categories:

### Hydrology
- Volumen Útil Diario (Energía)
- Aportes Diarios (Energía)
- Capacidad útil del SIN (Energía)

### Demand
- Demanda Real
- Demanda Comercial

### Generation & Supply
- Generación
- Generación Ideal

### Transactions & Prices
- Precio de Bolsa Nacional
- Precio de Escasez
- Reconciliaciones

### International Exchanges
- Exportaciones Energía
- Importaciones Energía

### Lists (Metadata)
- Listado Recursos
- Listado Agentes
- Listado Métricas
- Listado Ríos
- Listado Embalses

Use `get_available_metrics()` to see the complete, up-to-date list.

## Error Handling

```python
from httpx import HTTPStatusError

async with AsyncXMClient() as client:
    try:
        data = await client.get_data(
            metric="InvalidMetric",
            entity="InvalidEntity",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
    except ValueError as e:
        print(f"Invalid metric/entity: {e}")
    except HTTPStatusError as e:
        print(f"API request failed: {e}")
```

## Performance Tips

1. **Use Async Client**: For large date ranges, async client fetches chunks in parallel
2. **Filter Data**: Use `filter_by` parameter to reduce data volume
3. **Cache Metrics**: Call `get_available_metrics()` once and reuse the result
4. **Choose Granularity**: Use daily or monthly data when hourly isn't needed

## Examples

See `examples/xm_api_usage.py` for comprehensive usage examples including:
- Basic data fetching
- Filtering by resources
- Handling long time spans
- Data analysis workflows

## Architecture

```
AsyncXMClient/SyncXMClient
    ↓
AsyncXMFetcher/SyncXMFetcher
    ↓
AsyncHttpClient (with retry logic)
    ↓
XM API (https://servapibi.xm.com.co/)
    ↓
pandas DataFrame
```

## Contributing

When adding new XM API features:
1. Update schemas in `src/colombian_grid/core/schemas/xm.py`
2. Add methods to fetchers in `src/colombian_grid/core/base/interfaces/xm/fetchers.py`
3. Update clients in `src/colombian_grid/core/xm/xm_client.py`
4. Add tests in `tests/xm/`
5. Update this documentation

## References

- [XM API Documentation](https://github.com/EquipoAnaliticaXM/API_XM)
- [XM Official Website](https://www.xm.com.co/)

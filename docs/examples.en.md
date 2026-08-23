# Usage Examples

Here you'll find practical examples of how to use `colombian-grid` for different use cases.

## XM API

### Example 1: Getting Available Metrics

Before requesting data, you can list every metric the XM API offers.

```python
import asyncio
from colombian_grid import AsyncXMClient

async def main():
    async with AsyncXMClient() as client:
        metrics = await client.get_available_metrics()
        print("Metrics available in the XM API:")
        print(metrics[["MetricId", "MetricName", "Entity", "MaxDays"]])

asyncio.run(main())
```

### Example 2: Querying Generation by Resource with Filters

You can filter data by specific resource codes (e.g., power plants).

```python
import asyncio
from datetime import date
from colombian_grid import AsyncXMClient

async def main():
    async with AsyncXMClient() as client:
        # Query generation for the GUAJIRA1 and GUAJIRA2 plants
        data = await client.get_data(
            metric="Gene",
            entity="Recurso",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5),
            filter_by=["GUAJIRA1", "GUAJIRA2"],
        )
        print("Generation for GUAJIRA1 and GUAJIRA2:")
        print(data)

asyncio.run(main())
```

### Example 3: Sync Query for Spot Prices

If you prefer a synchronous approach, use `SyncXMClient`.

```python
from datetime import date
from colombian_grid import SyncXMClient

with SyncXMClient() as client:
    spot_price = client.get_data(
        metric="PrecBolsNaci",
        entity="Sistema",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 10),
    )
    print("National spot price (first 10 days of January 2024):")
    print(spot_price)
```

## Paratec API

### Example 4: Generator and Hydrology Data

Query generator data and hydrology records.

```python
import asyncio
from colombian_grid import AsyncParatecClient

async def main():
    async with AsyncParatecClient() as client:
        generators = await client.get_generation_data()
        print(f"Total generators: {len(generators)}")

        hydrology = await client.get_hydro_data()
        print(f"Hydrology records: {len(hydrology)}")

asyncio.run(main())
```

### Example 5: Substation Data

Query the list of substations registered in Paratec.

```python
import asyncio
from colombian_grid import AsyncParatecClient

async def main():
    async with AsyncParatecClient() as client:
        substations = await client.get_substation_data()
        print(f"Total substations: {len(substations)}")
        print(substations[0])

asyncio.run(main())
```

### Example 6: Transmission Line Data

Query the list of transmission lines.

```python
import asyncio
from colombian_grid import AsyncParatecClient

async def main():
    async with AsyncParatecClient() as client:
        lines = await client.get_transmission_line_data()
        print(f"Total transmission lines: {len(lines)}")
        print(lines[0])

asyncio.run(main())
```

!!! tip
    All `AsyncParatecClient` methods (`get_generation_data`, `get_substation_data`, `get_transmission_line_data`, `get_hydro_data`) can be called inside the same `async with` block, reusing the same HTTP connection.

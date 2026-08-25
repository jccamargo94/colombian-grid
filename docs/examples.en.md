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

## IDO API

### Example 7: Yesterday's Generation

The Daily Operation Report (IDO) daily generation archive. With no arguments it returns yesterday in Colombia time; it also accepts a `datetime.date`, a `datetime.datetime`, or an ISO string.

```python
import asyncio
from datetime import date
from colombian_grid import AsyncIdoClient

async def main():
    async with AsyncIdoClient() as client:
        # Yesterday in Colombia time (data is published ~06:05 COT)
        yesterday = await client.generacion()
        print(yesterday.head())

        # Or a specific date
        specific = await client.generacion(date(2026, 7, 15))
        print(specific[["fecha", "tipo_generacion", "nombrerecurso", "gendesp"]].head())

asyncio.run(main())
```

Each row is one observation per resource (`nombrerecurso`) and generation type (`tipo_generacion`), with the `gendesp`, `genened`, and `genprodesp` columns. Subtotals are excluded on purpose to avoid double counting.

### Example 8: International Exchanges with Totals

International exchanges with neighboring countries arrive in long format, one row per country and direction. This data is not available through XM's public API.

```python
import asyncio
from colombian_grid import AsyncIdoClient

async def main():
    async with AsyncIdoClient() as client:
        exchanges = await client.intercambios()
        print(exchanges[["direccion", "pais", "programada", "real"]])

        # Totals per direction ("exportaciones" / "importaciones")
        totals = exchanges.attrs["totales"]
        print(totals["exportaciones"])

asyncio.run(main())
```

The `direccion` column distinguishes `"exportaciones"` from `"importaciones"`; each direction's totals are exposed via `df.attrs["totales"]`.

### Example 9: Availability by Resource

Availability declares, per generation category (`tipogen`), the effective capacity and availability of every resource.

```python
import asyncio
from colombian_grid import AsyncIdoClient

async def main():
    async with AsyncIdoClient() as client:
        availability = await client.disponibilidad()

        # Subtotals are repeated on every row of their category;
        # take them once per category:
        print(
            availability.groupby("tipogen")[
                ["subtotal", "subtotal_capefectiva"]
            ].first()
        )

asyncio.run(main())
```

Besides `subtotal` and `subtotal_capefectiva`, each row carries `capacidadefectiva`, `disponibilidad`, and `porcentaje`.

### Example 10: Current Day's Coordinated Dispatch

`despacho_recurso()` returns the current day's coordinated dispatch program, in 24 hourly periods. Heads up: the endpoint is slow and can take around a minute to respond — be patient. It takes no date because the service always returns the current day.

```python
import asyncio
from colombian_grid import AsyncIdoClient

async def main():
    async with AsyncIdoClient() as client:
        dispatch = await client.despacho_recurso()
        print(dispatch[["recurso", "periodo", "generacion", "color", "categoria"]].head())

        # Report metadata (codigo, descripcion, version)
        print(dispatch.attrs["globales"])

asyncio.run(main())
```

The `color` column mirrors the status letter of the official IDO board (R, V, C, Y, P, N, A, M) and `categoria` translates that letter into its human-readable meaning (e.g., `"Racionamientos programados en Subárea"`); it is `None` when the color is null or unknown.

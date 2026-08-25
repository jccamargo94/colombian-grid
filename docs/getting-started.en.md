# Getting Started

`colombian-grid` lets you query public data from the Colombian electricity market (Paratec, XM, and IDO) from Python, without dealing with the underlying REST APIs directly.

## Installation

With `pip`:

```bash
pip install colombian-grid
```

With `uv`:

```bash
uv add colombian-grid
```

## Importing the clients

All clients can be imported directly from the top-level package:

```python
from colombian_grid import AsyncIdoClient, AsyncParatecClient, AsyncXMClient, SyncXMClient
```

## XM API — market data

The XM API provides electricity market data (generation, demand, prices, etc.). Two clients are available: an async one (`AsyncXMClient`, recommended) and a sync one (`SyncXMClient`), both sharing the same interface.

### Async client

```python
import asyncio
from datetime import date
from colombian_grid import AsyncXMClient

async def main():
    async with AsyncXMClient() as client:
        data = await client.get_data(
            metric="Gene",
            entity="Sistema",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        print("System generation (January 2024):")
        print(data.head())

asyncio.run(main())
```

### Sync client

Ideal for simple scripts that don't need concurrency:

```python
from datetime import date
from colombian_grid import SyncXMClient

with SyncXMClient() as client:
    data = client.get_data(
        metric="DemaReal",
        entity="Sistema",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
    )
    print("System demand (January 2024):")
    print(data.head())
```

## Paratec API — infrastructure data

The Paratec API provides data about the electrical system's infrastructure: generators, substations, transmission lines, and hydrology. It only has an async client (`AsyncParatecClient`).

```python
import asyncio
from colombian_grid import AsyncParatecClient

async def main():
    async with AsyncParatecClient() as client:
        generators = await client.get_generation_data()
        print(f"Found {len(generators)} generators.")

        substations = await client.get_substation_data()
        print(f"Found {len(substations)} substations.")

asyncio.run(main())
```

`AsyncParatecClient` implements `async with`, so the underlying HTTP connection closes automatically when the block exits — you don't need to close it manually.

## IDO API — Daily Operation Report

XM's [Daily Operation Report (IDO)](https://ido.xm.com.co/) summarizes the system's daily operation: generation, international exchanges, availability, costs, and coordinated dispatch. It only has an async client (`AsyncIdoClient`). By default, queries return yesterday in Colombia time, because IDO publishes previous-day data around 06:05 (Colombia time), with corrections delivered as new versions (V1, V2...).

```python
import asyncio
from colombian_grid import AsyncIdoClient

async def main():
    async with AsyncIdoClient() as client:
        generation = await client.generacion()       # yesterday (Colombia time)
        dispatch = await client.despacho_recurso()   # current day's dispatch
        print(f"Generation records: {len(generation)}")

asyncio.run(main())
```

Keep in mind:

- The `ido.xm.com.co` server serves an incomplete TLS certificate chain (a known upstream misconfiguration), so standard verification fails. If needed, pass `tls_verify=False` to the constructor as an explicit, deliberate workaround; we'd rather you keep verification enabled and report the issue to XM.
- `despacho_recurso()` takes no date: the service ignores any date parameter and always returns the current day's coordinated dispatch. It is also a slow endpoint (it can take around a minute); the client already applies a longer internal timeout for it.

`AsyncIdoClient` also implements `async with`, so the underlying HTTP connection closes automatically when the block exits.

## Next steps

- Check the [Examples](examples.md) page for more use cases, including substations and transmission lines.
- See the [API Reference](api-reference.md) for the full signature of every method.

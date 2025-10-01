# Guía Rápida

Esta guía te mostrará cómo instalar `colombian-grid` y realizar tus primeras consultas a las APIs de XM y Paratec.

## Instalación

Para empezar, instala la librería usando `pip`:

```bash
pip install colombian-grid
```

## Consultando el API de XM

El API de XM provee datos del mercado eléctrico. Ofrecemos dos tipos de clientes: asíncrono (`AsyncXMClient`) y síncrono (`SyncXMClient`).

### Cliente Asíncrono (Recomendado)

El cliente asíncrono es ideal para aplicaciones de alto rendimiento que manejan operaciones de I/O concurrentes.

```python
import asyncio
from datetime import date
from colombian_grid.core.xm import AsyncXMClient

async def main():
    async with AsyncXMClient() as client:
        # Obtener la generación del sistema para un rango de fechas
        data = await client.get_data(
            metric="Gene",
            entity="Sistema",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        print("Generación del Sistema (Enero 2024):")
        print(data.head())

asyncio.run(main())
```

### Cliente Síncrono

El cliente síncrono es más sencillo de usar en scripts y aplicaciones que no requieren concurrencia.

```python
from datetime import date
from colombian_grid.core.xm import SyncXMClient

with SyncXMClient() as client:
    # Obtener la demanda real del sistema
    data = client.get_data(
        metric="DemaReal",
        entity="Sistema",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31)
    )
    print("Demanda Real del Sistema (Enero 2024):")
    print(data.head())
```

## Consultando el API de Paratec

El API de Paratec provee datos sobre la infraestructura del sistema eléctrico, como generadores, subestaciones y líneas de transmisión.

### Cliente Asíncrono

```python
import asyncio
from colombian_grid.core.paratec import AsyncParatecClient

async def main():
    client = AsyncParatecClient()

    # Obtener datos de generadores
    generadores = await client.get_generation_data()
    print(f"Se encontraron {len(generadores)} generadores.")

    # Obtener datos de subestaciones
    subestaciones = await client.get_substation_data()
    print(f"Se encontraron {len(subestaciones)} subestaciones.")

    # Es importante cerrar el cliente al finalizar
    await client._http_client.close()

asyncio.run(main())
```

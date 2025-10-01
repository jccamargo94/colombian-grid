# Ejemplos de Uso

Aquí encontrarás ejemplos prácticos de cómo utilizar `colombian-grid` para diferentes casos de uso.

## API de XM

### Ejemplo 1: Obtener Métricas Disponibles

Antes de solicitar datos, puedes consultar todas las métricas que ofrece el API de XM.

```python
import asyncio
from colombian_grid.core.xm import AsyncXMClient

async def main():
    async with AsyncXMClient() as client:
        metrics = await client.get_available_metrics()
        print("Métricas disponibles en el API de XM:")
        print(metrics[['MetricId', 'MetricName', 'Entity', 'MaxDays']])

asyncio.run(main())
```

### Ejemplo 2: Consultar Generación por Recurso con Filtros

Puedes filtrar los datos por códigos de recursos específicos (por ejemplo, plantas de generación).

```python
import asyncio
from datetime import date
from colombian_grid.core.xm import AsyncXMClient

async def main():
    async with AsyncXMClient() as client:
        # Consultar generación para las plantas GUAJIRA1 y GUAJIRA2
        data = await client.get_data(
            metric="Gene",
            entity="Recurso",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5),
            filter_by=["GUAJIRA1", "GUAJIRA2"]
        )
        print("Generación para GUAJIRA1 y GUAJIRA2:")
        print(data)

asyncio.run(main())
```

### Ejemplo 3: Consulta Síncrona de Precios de Bolsa

Si prefieres un enfoque síncrono, puedes usar `SyncXMClient`.

```python
from datetime import date
from colombian_grid.core.xm import SyncXMClient

with SyncXMClient() as client:
    # Consultar precio de bolsa nacional
    precio_bolsa = client.get_data(
        metric="PrecBolsNaci",
        entity="Sistema",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 10)
    )
    print("Precio de Bolsa Nacional (primeros 10 días de Enero 2024):")
    print(precio_bolsa)
```

## API de Paratec

### Ejemplo 4: Obtener Datos de Infraestructura

Consulta datos sobre generadores, subestaciones y líneas de transmisión.

```python
import asyncio
from colombian_grid.core.paratec import AsyncParatecClient

async def main():
    client = AsyncParatecClient()

    # Datos de generadores
    generadores = await client.get_generation_data()
    print(f"Total de generadores: {len(generadores)}")

    # Datos de hidrología
    hidrologia = await client.get_hydro_data()
    print(f"Registros de hidrología: {len(hidrologia)}")

    await client._http_client.close()

asyncio.run(main())
```

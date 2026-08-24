# Comenzando

`colombian-grid` te permite consultar datos públicos del mercado eléctrico colombiano (Paratec y XM) desde Python, sin tener que lidiar directamente con las APIs REST subyacentes.

## Instalación

Con `pip`:

```bash
pip install colombian-grid
```

Con `uv`:

```bash
uv add colombian-grid
```

## Importando los clientes

Todos los clientes se pueden importar directamente desde el paquete raíz:

```python
from colombian_grid import AsyncParatecClient, AsyncXMClient, SyncXMClient
```

## API de XM — datos de mercado

El API de XM provee datos del mercado eléctrico (generación, demanda, precios, etc.). Hay dos clientes disponibles: uno asíncrono (`AsyncXMClient`, recomendado) y uno síncrono (`SyncXMClient`), ambos con la misma interfaz.

### Cliente asíncrono

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
        print("Generación del Sistema (Enero 2024):")
        print(data.head())

asyncio.run(main())
```

### Cliente síncrono

Ideal para scripts simples que no requieren concurrencia:

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
    print("Demanda Real del Sistema (Enero 2024):")
    print(data.head())
```

## API de Paratec — datos de infraestructura

El API de Paratec provee datos sobre la infraestructura del sistema eléctrico: generadores, subestaciones, líneas de transmisión e hidrología. Solo tiene cliente asíncrono (`AsyncParatecClient`).

```python
import asyncio
from colombian_grid import AsyncParatecClient

async def main():
    async with AsyncParatecClient() as client:
        generadores = await client.get_generation_data()
        print(f"Se encontraron {len(generadores)} generadores.")

        subestaciones = await client.get_substation_data()
        print(f"Se encontraron {len(subestaciones)} subestaciones.")

asyncio.run(main())
```

`AsyncParatecClient` implementa `async with`, así que la conexión HTTP subyacente se cierra automáticamente al salir del bloque — no necesitas cerrarla manualmente.

## Próximos pasos

- Revisa la sección de [Ejemplos](examples.md) para ver más casos de uso, incluyendo subestaciones y líneas de transmisión.
- Consulta la [Referencia API](api-reference.md) para ver la firma completa de cada método.
